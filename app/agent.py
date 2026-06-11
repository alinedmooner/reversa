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
from google.adk.tools import VertexAiSearchTool, load_memory

from .money_graph import trace_funds
from .recall import issue_recall

# Vertex no acepta alias de AI Studio (gemini-flash-latest): ID versionado.
MODEL = "gemini-2.5-flash"

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


def get_current_time() -> dict:
    """Devuelve la fecha y hora actual real en Colombia (America/Bogota), en formato ISO 8601.
    Úsala para resolver expresiones de tiempo relativas (por ejemplo 'hace 10 minutos')
    y calcular el valor absoluto de fecha_hora."""
    return {"current_time": datetime.now(ZoneInfo("America/Bogota")).isoformat()}


intake_agent = LlmAgent(
    name="intake",
    model=MODEL,
    description="Convierte el reporte de la víctima en datos estructurados del caso.",
    instruction=(
        "Eres el agente de intake de Reversa. Del reporte de la víctima extrae SOLO un JSON "
        "con: monto, llave_destino, fecha_hora, tipo_fraude (coacción | phishing | suplantación | otro). "
        "Para tiempos relativos ('hace 10 minutos'), llama a get_current_time y calcula el "
        "timestamp absoluto ISO 8601. Responde ÚNICAMENTE con el JSON."
    ),
    tools=[get_current_time],
    output_key="intake_json",
)

tracing_agent = LlmAgent(
    name="tracing",
    model=MODEL,
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
    model=MODEL,
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
    model=MODEL,
    description="Redacta el expediente final del caso para el banco/regulador.",
    instruction=(
        "Eres el agente de evidencia de Reversa. Redacta el expediente final del caso en "
        "español, claro y auditable, con estas secciones:\n"
        "1. Datos del reporte: {intake_json}\n"
        "2. Rastreo del dinero: {trace_result}\n"
        "3. Acción ejecutada: {action_result}\n"
        "4. Conclusión: estado final de los fondos y siguiente paso recomendado para el banco.\n"
        "IMPORTANTE: el estado final de los fondos debe reconciliar el rastreo con la acción "
        "ejecutada. Si la acción reporta BLOQUEO EMITIDO, el estado final es FONDOS BLOQUEADOS "
        "(no 'interceptable'): el rastreo refleja el estado ANTES de la acción.\n"
        "Termina el expediente con una sección '5. Inteligencia de mulas' que liste "
        "explícitamente las llaves confirmadas como cuentas mula en este caso, con banco, "
        "dueño y case_id, para alimentar la memoria institucional.\n"
        "Antes de redactar la sección de 'Siguiente paso recomendado', consulta el manual "
        "normativo (herramienta de búsqueda) y fundamenta la recomendación en lo que diga: "
        "flujo camt.056 → camt.029 → pacs.004, SLA de seguimiento, y la diferencia Brasil "
        "(MED) vs Colombia (sin mecanismo equivalente). Cita el manual cuando afirmes algo "
        "normativo."
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
