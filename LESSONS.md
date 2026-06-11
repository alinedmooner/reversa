# LESSONS — Prototipo Reversa

Checklist práctico de gotchas encontrados durante el prototipo (google-adk 2.2.0,
Vertex AI, junio 2026), organizado por tema, para no repetirlos en el build final.

> Nota (repo final): los paths `reversa/` de este documento corresponden a
> `app/` en este repo (p. ej. `reversa/a2a_server.py` → `app/a2a_server.py`,
> `reversa/.env` → `app/.env`, `reversa/requirements.txt` → `app/requirements.txt`).

## Modelos (Gemini en Vertex)

- [ ] Vertex NO acepta alias de AI Studio como `gemini-flash-latest`. Usar IDs
      versionados: `gemini-2.5-flash`.
- [ ] El error `No API key was provided... ai.google.dev` significa que un proceso
      cayó al path de AI Studio: le faltan las env vars de Vertex
      (`GOOGLE_GENAI_USE_VERTEXAI=TRUE`, `GOOGLE_CLOUD_PROJECT`,
      `GOOGLE_CLOUD_LOCATION`). Buscar en el log de CADA proceso (web, uvicorn,
      contenedor) para identificar cuál fue.

## Carga de entorno (.env)

- [ ] Solo `adk web` / `adk run` auto-cargan el `.env` por carpeta de agente.
      uvicorn pelado, contenedores y CI necesitan env explícito — en este repo,
      `reversa/a2a_server.py` carga `reversa/.env` vía `python-dotenv` en import.
- [ ] El `.env` por agente se carga DESPUÉS del arranque del servidor: servicios
      de plataforma como `--memory_service_uri="agentengine://..."` necesitan
      `GOOGLE_CLOUD_PROJECT`/`GOOGLE_CLOUD_LOCATION` en el entorno del proceso
      (inline en el comando o exportadas), no en el `.env`.

## Deploy a Agent Engine

- [ ] `adk deploy agent_engine` requiere `google-cloud-aiplatform[agent_engines]`
      instalado localmente (falla con `No module named 'vertexai'` si no está).
- [ ] Instalar aiplatform sube opentelemetry a >=1.42, rompiendo el pin de
      google-adk 2.2.0 — fijar `opentelemetry-api/sdk/exporter-otlp-proto-http`
      a 1.41.1.
- [ ] Habilitar `cloudbuild.googleapis.com` y `artifactregistry.googleapis.com`
      ANTES del primer deploy: si faltan, el error es un opaco
      `{'code': 13, 'message': 'INTERNAL'}`.
- [ ] El contenedor necesita su propio `reversa/requirements.txt` con
      `google-adk[a2a]==2.2.0`: el requirements auto-generado solo pone
      `google-adk` base y el arranque crashea con `No module named 'a2a'`.
- [ ] `--staging_bucket` está deprecado/ignorado en ADK 2.2.0.
- [ ] Crashes del contenedor se diagnostican en Cloud Logging
      (`resource.type="aiplatform.googleapis.com/ReasoningEngine"`); el error del
      CLI no trae la causa.
- [ ] Un deploy fallido LIMPIA su instancia: cada retry crea un resource ID
      nuevo — actualizar toda referencia (tests, URIs de memoria).
- [ ] Cliente remoto: `vertexai.init(...)` + `agent_engines.get(resource_name)` +
      `create_session` / `stream_query`.

## Multi-agente (SequentialAgent)

- [ ] Pasar estado entre etapas con `output_key` + placeholders `{clave}` en las
      instructions de los agentes siguientes.
- [ ] Reconciliar estado obsoleto en el reporter final: el resultado del rastreo
      refleja el estado ANTES de la acción (decía "interceptable" después de
      bloquear) — instruir la reconciliación explícitamente.

## Memory Bank

- [ ] Lo respalda una instancia de Agent Engine (puede estar VACÍA:
      `vertexai.agent_engines.create(display_name=...)` sin agente).
- [ ] Conectar el dev server con `adk web --memory_service_uri="agentengine://ID"`
      (más las env vars de proyecto/región en el proceso, ver arriba).
- [ ] Auto-guardado limpio en ADK 2.2.0: `after_agent_callback` async que llama
      `await callback_context.add_session_to_memory()`. Tolerar `ValueError`
      cuando no hay servicio de memoria configurado.
- [ ] La generación de memorias es asíncrona (~1–2 min): no esperar recall
      inmediato tras cerrar un caso.
- [ ] Recuperación vía la tool integrada `load_memory`
      (`from google.adk.tools import load_memory`).

## A2A

- [ ] El `port` de `to_a2a()` es solo metadata del agent card — el puerto real lo
      pone `--port` de uvicorn. Mantenerlos iguales o el card publica URL errada.
- [ ] El lado servidor necesita `sse-starlette` (extra `a2a-sdk[http-server]`),
      que `google-adk[a2a]` NO arrastra — ImportError al primer arranque.
- [ ] El servidor A2A no recarga código de agentes en caliente: reiniciar uvicorn
      tras cada cambio (incluye cambios de tools en el pipeline).
- [ ] En modo Vertex, el convertidor A2A de ADK 2.2.0 mete `Part.part_metadata` y
      la API de Vertex lo RECHAZA (`part_metadata... only supported in Gemini
      Developer API mode`). Workaround: `before_model_callback` que borra
      `part_metadata` de los contents (ver `reversa/a2a_server.py`).
- [ ] Delegar-y-resumir: con `sub_agents`, `transfer_to_agent` CEDE la
      conversación y el agente padre no retoma para resumir. Para "delega, espera
      y resume" usar `AgentTool(agent=remote_agent)` en `tools`.
- [ ] `RemoteA2aAgent` es experimental en 2.2.0 (warning en import); card en
      `/.well-known/agent-card.json` (constante `AGENT_CARD_WELL_KNOWN_PATH`).
- [ ] Un GET al endpoint JSON-RPC devuelve 405 — es normal, no es un puerto
      equivocado; verificar con el agent card, no con `GET /`.

## Search / RAG (Vertex AI Search · Discovery Engine)

- [ ] Discovery Engine RECHAZA `text/markdown`: subir como `text/plain`
      (`gcloud storage cp --content-type=text/plain`), PDF u otro tipo aceptado.
- [ ] Un import puede terminar "done" CON el documento rechazado: revisar
      `errorSamples` y `successCount` en la operación, no solo `done: true`.
- [ ] `VertexAiSearchTool` acepta `data_store_id` (resource name completo)
      directamente — no hace falta crear engine/app de búsqueda.
- [ ] Tools integradas (VertexAiSearchTool, etc.) NO se mezclan con function
      tools en el mismo agente — dedicar un agente del pipeline a la búsqueda.
- [ ] Verificar grounding real revisando `groundingMetadata.groundingChunks` en
      los eventos, no solo leyendo la respuesta.
- [ ] La creación del data store (global) es inmediata; la indexación tarda
      minutos — pollear la operación de import.

## Estado y demos

- [ ] El grafo mock (`MONEY_GRAPH`) vive en memoria POR PROCESO: un recall
      emitido en el servidor A2A persiste hasta reiniciar ese proceso (la demo
      dirá "ya bloqueada"). Reiniciar procesos para una demo limpia.
- [ ] `curl http://localhost:8000/list-apps` confirma qué agentes descubrió
      adk web; la UI vive en `/dev-ui/` (GET / responde 307).
