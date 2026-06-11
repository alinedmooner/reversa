# Project name used for resource naming
project_name = "reversa"

# Proyecto único (hackathon): CICD, staging y prod apuntan todos a
# reversa-datamirai. El deploy real lo hace el workflow de staging en cada
# push a main; el de prod queda solo como workflow_dispatch manual.
prod_project_id = "reversa-datamirai"

staging_project_id = "reversa-datamirai"

cicd_runner_project_id = "reversa-datamirai"

repository_owner = "alinedmooner"

# Name of the repository (GitHub)
repository_name = "reversa"

# The Google Cloud region you will use to deploy the infrastructure
region = "us-central1"

# Roles del SA de la app: los defaults del scaffold + Discovery Engine,
# necesario para que el agente evidence consulte el data store de Vertex AI
# Search (reversa-normativa) desde Agent Engine.
app_sa_roles = [
  "roles/aiplatform.user",
  "roles/logging.logWriter",
  "roles/cloudtrace.agent",
  "roles/storage.admin",
  "roles/serviceusage.serviceUsageConsumer",
  "roles/discoveryengine.viewer",
]
