"""Expone el pipeline de Reversa como servicio A2A (Agent-to-Agent).

Otros agentes (p. ej. el agente de fraude de un banco) pueden descubrirlo vía su
agent card y delegarle casos. Servir con:

    uvicorn app.a2a_server:a2a_app --host localhost --port 8001

Notas (LESSONS.md — A2A):
- El servidor necesita sse-starlette (no lo arrastra google-adk[a2a]).
- El `port` de to_a2a es solo metadata del agent card: mantenerlo igual al
  --port de uvicorn o el card publica una URL errada.
- No recarga código en caliente: reiniciar uvicorn tras cada cambio.
- El workaround de part_metadata para modo Vertex se aplica en app/agent.py
  (sobre la definición compartida), así cubre también el path de Agent Engine.
- Usa los servicios in-memory por defecto de to_a2a; conectar el Memory Bank
  requeriría construir un Runner completo a mano (to_a2a no acepta un memory
  service directo en ADK 2.2.0).
"""

from pathlib import Path

from dotenv import load_dotenv

# uvicorn no auto-carga el .env del agente: carga explícita antes de importar
# el pipeline (LESSONS.md — Carga de entorno).
load_dotenv(Path(__file__).parent / ".env")

from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .agent import root_agent

a2a_app = to_a2a(root_agent, port=8001)
