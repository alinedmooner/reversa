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

locals {
  cicd_services = [
    "cloudbuild.googleapis.com",
    "aiplatform.googleapis.com",
    "serviceusage.googleapis.com",
    "bigquery.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudtrace.googleapis.com",
    "telemetry.googleapis.com",
  ]

  deploy_project_services = [
    "aiplatform.googleapis.com",
    # LESSONS.md (Deploy): cloudbuild + artifactregistry deben estar habilitadas
    # ANTES del primer deploy a Agent Engine (error opaco INTERNAL si faltan).
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    # Vertex AI Search (manual normativo del agente evidence).
    "discoveryengine.googleapis.com",
    "run.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "bigquery.googleapis.com",
    "serviceusage.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "telemetry.googleapis.com",
  ]

  # Proyecto único: si staging y prod son el MISMO proyecto, se colapsa a un
  # solo entorno ("prod") — evita colisiones de nombres (SAs, datasets BQ,
  # sinks de logging) y un segundo reasoning engine siempre encendido.
  single_project = var.staging_project_id == var.prod_project_id

  deploy_project_ids = local.single_project ? {
    prod = var.prod_project_id
    } : {
    prod    = var.prod_project_id
    staging = var.staging_project_id
  }

  # Clave a usar donde el scaffold espera el entorno "staging".
  staging_key = local.single_project ? "prod" : "staging"

  all_project_ids = [
    var.cicd_runner_project_id,
    var.prod_project_id,
    var.staging_project_id
  ]

}

