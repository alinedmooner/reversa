"""Agente interno de fraude del Banco Andes (consumidor A2A de Reversa).

Simula el agente de un banco que, ante el reporte de un cliente, delega la
investigación y recuperación al servicio remoto Reversa vía protocolo A2A.
Requiere el servidor A2A corriendo:

    uvicorn app.a2a_server:a2a_app --host localhost --port 8001
"""

from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)
from google.adk.tools.agent_tool import AgentTool

reversa_remote = RemoteA2aAgent(
    name="reversa",
    description=(
        "Servicio autónomo de rastreo y recuperación de fraude en pagos "
        "inmediatos (Bre-B/Pix)."
    ),
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)

root_agent = LlmAgent(
    name="banco_andes_fraude",
    model="gemini-2.5-flash",
    instruction=(
        "Eres el agente interno de gestión de fraude del Banco Andes. Cuando un "
        "cliente reporta un fraude en un pago inmediato, delega INMEDIATAMENTE la "
        "investigación y recuperación al agente remoto reversa (pásale el reporte "
        "completo del cliente). Cuando reversa termine, entrega al cliente un resumen "
        "ejecutivo del expediente: qué se encontró, qué acción se tomó y el estado de "
        "su dinero."
    ),
    # AgentTool (no sub_agents): la transferencia a sub-agente cede la conversación
    # y el resumen ejecutivo nunca se ejecutaría; como tool, reversa devuelve el
    # expediente y este agente retoma el control para resumirlo.
    tools=[AgentTool(agent=reversa_remote)],
)
