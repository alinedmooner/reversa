"""Pipeline multi-agente de Reversa: intake → rastreo → acción → expediente.

Recuperación autónoma de fraude en rieles de pago inmediato (Bre-B / Pix):
estructura el reporte de la víctima, rastrea el dinero por la red de mulas,
emite el bloqueo camt.056 y redacta el expediente auditable del caso.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

# Solo `adk web`/`adk run` auto-cargan el .env por carpeta de agente; uvicorn,
# contenedores, tests y CI necesitan la carga explícita ANTES de construir los
# agentes (LESSONS.md — Carga de entorno).
load_dotenv(Path(__file__).parent / ".env")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import VertexAiSearchTool, load_memory
from google.genai import types

from .money_graph import trace_funds
from .recall import issue_recall

# Vertex no acepta alias de AI Studio (gemini-flash-latest): ID versionado.
MODEL = "gemini-2.5-flash"


def _gemini() -> Gemini:
    """Modelo con reintentos con backoff para 429 RESOURCE_EXHAUSTED.

    Proyecto nuevo = cuota Gemini baja; el pipeline encadena 4+ llamadas por
    caso y sin retry una ráfaga de 429 aborta el caso entero
    (TASK_STATE_FAILED en Agent Engine). ~60s de presupuesto de backoff.
    """
    return Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(
            attempts=6, initial_delay=2, max_delay=30
        ),
    )

# Data store de Vertex AI Search con el manual normativo (docs/).
_project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
DATA_STORE_ID = os.environ.get(
    "REVERSA_DATA_STORE_ID",
    "projects/{project}/locations/global/collections/default_collection/"
    "dataStores/reversa-normativa".format(project=_project),
)
if not _project and "REVERSA_DATA_STORE_ID" not in os.environ:
    logging.warning(
        "Ni GOOGLE_CLOUD_PROJECT ni REVERSA_DATA_STORE_ID están configurados: "
        "la búsqueda normativa (agente evidence) fallará con un data store "
        "malformado (%s).",
        DATA_STORE_ID,
    )


def get_current_time(timezone: str = "America/Bogota") -> dict:
    """Devuelve la fecha y hora actual real en la zona horaria del caso, en formato ISO 8601.

    Úsala para resolver expresiones de tiempo relativas ('hace 10 minutos',
    'há 10 minutos') y calcular el valor absoluto de fecha_hora. Pasa
    timezone='America/Sao_Paulo' para casos Pix (Brasil) y
    timezone='America/Bogota' para casos Bre-B (Colombia).
    """
    try:
        tz = ZoneInfo(timezone)
    except Exception:
        tz = ZoneInfo("America/Bogota")
    return {"current_time": datetime.now(tz).isoformat(), "timezone": str(tz)}


intake_agent = LlmAgent(
    name="intake",
    model=_gemini(),
    description="Convierte el reporte de la víctima en datos estructurados del caso.",
    instruction=(
        "Eres el agente de intake de Reversa. El reporte de la víctima puede venir en "
        "español (riel Bre-B, Colombia) o en portugués brasileño (riel Pix, Brasil). "
        "Extrae SOLO un JSON con: monto, llave_destino (la llave/chave reportada, tal cual), "
        "fecha_hora, tipo_fraude (coacción | phishing | suplantación | otro), "
        "rail y idioma_reporte.\n"
        "Detección del riel: rail='PIX_BR' si el reporte es de Pix Brasil (portugués, "
        "montos en R$/reais, chaves tipo CPF 000.000.000-00, celular +55 o aleatoria/EVP "
        "tipo UUID, 'golpe'); rail='BREB_CO' si es de Bre-B Colombia (español, pesos, "
        "llaves numéricas). idioma_reporte='pt' o 'es' según el idioma del reporte.\n"
        "Para tiempos relativos ('hace 10 minutos', 'há 10 minutos'), llama a "
        "get_current_time con timezone='America/Sao_Paulo' si rail=PIX_BR o "
        "timezone='America/Bogota' si rail=BREB_CO, y calcula el timestamp absoluto "
        "ISO 8601. Responde ÚNICAMENTE con el JSON."
    ),
    tools=[get_current_time],
    output_key="intake_json",
)

tracing_agent = LlmAgent(
    name="tracing",
    model=_gemini(),
    description="Rastrea a dónde se movió el dinero a través de cuentas mula.",
    instruction=(
        "Eres el agente de rastreo de Reversa. Datos del caso: {intake_json}\n"
        "Llama a trace_funds con la llave_destino y resume: la ruta salto por salto "
        "(llave, dueño, banco), dónde está el dinero ahora (current_location) y su estado "
        "(interceptable o bloqueado).\n"
        "Después de rastrear la ruta, llama a load_memory buscando las llaves de la ruta "
        "para verificar si alguna cuenta ya es una mula conocida de casos anteriores. Si hay "
        "coincidencias, márcalas en tu resumen como MULA CONOCIDA (con el caso previo) e "
        "indica que la red ya estaba identificada."
    ),
    tools=[trace_funds, load_memory],
    output_key="trace_result",
)

action_agent = LlmAgent(
    name="action",
    model=_gemini(),
    description="Ejecuta el bloqueo camt.056 cuando los fondos son interceptables.",
    instruction=(
        "Eres el agente de acción de Reversa. Datos del caso: {intake_json}\n"
        "Resultado del rastreo: {trace_result}\n"
        "Si el estado dice 'FONDOS DETENIDOS - interceptable', llama INMEDIATAMENTE a "
        "issue_recall con la llave de current_location y el monto — no pidas permiso, "
        "la velocidad es crítica. Si ya están bloqueados o no son interceptables, no hagas nada. "
        "Reporta la acción tomada (message_id, case_id, banco) o por qué no se actuó."
    ),
    tools=[issue_recall],
    output_key="action_result",
)

evidence_agent = LlmAgent(
    name="evidence",
    model=_gemini(),
    description="Redacta el expediente final del caso para el banco/regulador.",
    instruction=(
        "Eres el agente de evidencia de Reversa. Redacta el expediente final del caso "
        "EN EL IDIOMA DEL REPORTE de la víctima (idioma_reporte del intake: 'pt' → "
        "portugués brasileño; 'es' → español), claro y auditable, con estas secciones "
        "(títulos traducidos al idioma del expediente):\n"
        "1. Datos del reporte: {intake_json}\n"
        "2. Rastreo del dinero: {trace_result}\n"
        "3. Acción ejecutada: {action_result}\n"
        "4. Conclusión: estado final de los fondos y siguiente paso recomendado para el banco.\n"
        "IMPORTANTE: el estado final de los fondos debe reconciliar el rastreo con la acción "
        "ejecutada. Si la acción reporta BLOQUEO EMITIDO, el estado final es FONDOS BLOQUEADOS "
        "(no 'interceptable'): el rastreo refleja el estado ANTES de la acción.\n"
        "Termina el expediente con una sección '5. Inteligencia de mulas' que liste "
        "explícitamente las llaves/chaves confirmadas como cuentas mula en este caso, con "
        "banco, dueño y case_id, para alimentar la memoria institucional.\n"
        "Antes de redactar la sección de 'Siguiente paso recomendado', consulta el manual "
        "normativo (herramienta de búsqueda) y fundamenta la recomendación SEGÚN EL RAIL "
        "del caso: para rail=PIX_BR, enmarca el recall camt.056 dentro del MED del Banco "
        "Central do Brasil (flujo camt.056 → camt.029 → pacs.004, SLA de seguimiento, y el "
        "contexto MED 2.0 de rastreo multi-capa); para rail=BREB_CO, destaca que Bre-B no "
        "tiene mecanismo equivalente al MED y que la gestión pasa por la entidad bajo "
        "vigilancia de la SFC. Cita el manual cuando afirmes algo normativo."
    ),
    # Tools integradas no se mezclan con function tools en el mismo agente:
    # la búsqueda normativa vive dedicada en esta etapa (LESSONS.md — Search/RAG).
    tools=[VertexAiSearchTool(data_store_id=DATA_STORE_ID)],
    output_key="case_report",
)


async def save_case_to_memory(callback_context: CallbackContext) -> None:
    """Guarda la sesión completada en el Memory Bank (inteligencia de mulas).

    Si el servidor corre sin servicio de memoria (p. ej. adk web sin
    --memory_service_uri), no interrumpe el pipeline.
    """
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        pass


root_agent = SequentialAgent(
    name="reversa_pipeline",
    description="Pipeline autónomo de recuperación de fraude: intake → rastreo → acción → expediente.",
    sub_agents=[intake_agent, tracing_agent, action_agent, evidence_agent],
    after_agent_callback=save_case_to_memory,
)


def _strip_part_metadata(callback_context, llm_request):
    """Quita part_metadata de los contenidos antes de llamar al modelo.

    El convertidor A2A de ADK 2.2.0 copia la metadata de los mensajes A2A a
    Part.part_metadata, pero la API de Vertex la rechaza (solo la soporta el
    Gemini Developer API). Se aplica aquí, sobre la definición compartida de
    los agentes, para cubrir TODOS los caminos A2A (uvicorn local y Agent
    Engine); fuera de A2A es un no-op (LESSONS.md — A2A).
    """
    for content in llm_request.contents or []:
        for part in content.parts or []:
            if getattr(part, "part_metadata", None):
                part.part_metadata = None
    return None


def _patch_agents(agent):
    if isinstance(agent, LlmAgent):
        agent.before_model_callback = _strip_part_metadata
    for sub in agent.sub_agents:
        _patch_agents(sub)


_patch_agents(root_agent)

app = App(
    root_agent=root_agent,
    name="app",
)
