# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import os
import time

from locust import HttpUser, between, task

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Vertex AI and load agent config
with open("deployment_metadata.json", encoding="utf-8") as f:
    remote_agent_engine_id = json.load(f)["remote_agent_engine_id"]

parts = remote_agent_engine_id.split("/")
project_id = parts[1]
location = parts[3]
engine_id = parts[5]

# Convert remote agent engine ID to URLs
base_url = f"https://{location}-aiplatform.googleapis.com"
a2a_base_path = f"/v1beta1/projects/{project_id}/locations/{location}/reasoningEngines/{engine_id}/a2a/v1"

logger.info("Using remote agent engine ID: %s", remote_agent_engine_id)
logger.info("Using base URL: %s", base_url)
logger.info("Using API base path: %s", a2a_base_path)


def _collect_text(node: object) -> list[str]:
    """Recolecta recursivamente los valores de claves 'text' (partes A2A)."""
    texts: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "text" and isinstance(value, str):
                texts.append(value)
            else:
                texts.extend(_collect_text(value))
    elif isinstance(node, list):
        for item in node:
            texts.extend(_collect_text(item))
    return texts


class SendMessageUser(HttpUser):
    """Simulates a user interacting with the send message API."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    host = base_url  # Set the base host URL for Locust

    @task
    def send_message_and_poll(self) -> None:
        """Corre UN caso E2E y termina la corrida (gate determinista de CI).

        Éxito, fallo o timeout: el resultado queda registrado en las stats
        (y en el exit code de locust); no se encolan casos adicionales.
        """
        try:
            self._run_case()
        finally:
            self.environment.runner.quit()

    def _run_case(self) -> None:
        """Sends a message and polls for completion, asserting a final dossier."""
        headers = {"Content-Type": "application/json"}
        headers["Authorization"] = f"Bearer {os.environ['_AUTH_TOKEN']}"

        data = {
            "message": {
                "messageId": "msg-id",
                "content": [{"text": "Me hicieron un secuestro relámpago, transferí $11.000.000 a la llave 3001234567 hace 10 minutos."}],
                "role": "ROLE_USER",
            }
        }

        e2e_start_time = time.time()
        with self.client.post(
            f"{a2a_base_path}/message:send",
            headers=headers,
            json=data,
            catch_response=True,
            name="/v1/message:send",
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Send failed with status code: {response.status_code}"
                )
                return

            response.success()
            response_data = response.json()

            # Extract task ID
            try:
                task_id = response_data["task"]["id"]
            except (KeyError, TypeError) as e:
                logger.error(f"Failed to extract task ID: {e}")
                return

        # Poll for task completion.
        # El pipeline encadena 4 agentes (LLM + tools + RAG + expediente
        # largo): un caso legítimo tarda 1-3 minutos. Presupuesto: 48 polls
        # x 5s = 240s por tarea (los defaults del scaffold — 20x0.5s — están
        # calibrados para un agente trivial).
        max_polls = 48  # Maximum number of poll attempts
        poll_interval = 5.0  # Seconds between polls
        poll_count = 0

        while poll_count < max_polls:
            poll_count += 1
            time.sleep(poll_interval)

            with self.client.get(
                f"{a2a_base_path}/tasks/{task_id}",
                headers=headers,
                catch_response=True,
                name="/v1/tasks/{id}",
            ) as poll_response:
                if poll_response.status_code != 200:
                    poll_response.failure(
                        f"Poll failed with status code: {poll_response.status_code}"
                    )
                    return

                poll_data = poll_response.json()

                try:
                    task_state = poll_data["status"]["state"]
                except (KeyError, TypeError) as e:
                    logger.error(f"Failed to extract task state: {e}")
                    poll_response.failure(f"Invalid response format: {e}")
                    return

                # Check if task is complete
                if task_state in ["TASK_STATE_COMPLETED"]:
                    # Gate E2E real: la tarea debe terminar CON expediente
                    # (artefactos con texto sustancial), no solo completar.
                    dossier = "\n".join(_collect_text(poll_data.get("artifacts")))
                    if len(dossier) < 200:
                        poll_response.failure(
                            "Task completed without a final dossier "
                            f"(artifact text: {len(dossier)} chars)"
                        )
                        return
                    poll_response.success()

                    # Measure end-to-end time
                    e2e_duration = (time.time() - e2e_start_time) * 1000

                    # Fire custom event for end-to-end metrics
                    self.environment.events.request.fire(
                        request_type="E2E",
                        name="message:send_and_complete",
                        response_time=e2e_duration,
                        response_length=len(json.dumps(poll_data)),
                        response=poll_response,
                        context={"poll_count": poll_count},
                    )
                    return

                elif task_state in ["TASK_STATE_WORKING"]:
                    poll_response.success()

                else:
                    poll_response.failure(f"Task failed with state: {task_state}")
                    return

        # Timeout - task didn't complete in time
        self.environment.events.request.fire(
            request_type="TIMEOUT",
            name="message:timeout",
            response_time=(time.time() - e2e_start_time) * 1000,
            response_length=0,
            response=None,
            context={"poll_count": poll_count},
            exception=TimeoutError(f"Task did not complete after {max_polls} polls"),
        )
