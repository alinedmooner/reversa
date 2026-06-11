# Reversa

Recuperación autónoma de fraude en rieles de pago inmediato (Bre-B / Pix).
Pipeline multi-agente (ADK + A2A): intake → rastreo del dinero por cuentas mula →
bloqueo camt.056 → expediente auditable con fundamento normativo (Vertex AI Search)
y memoria institucional de mulas (Memory Bank).

Scaffold generado con [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) versión `0.41.3` (template `adk_a2a`, CI/CD GitHub Actions). Ver gotchas aplicados en [LESSONS.md](LESSONS.md).

## Why Reversa — the research

Instant payment rails (100+ jurisdictions live) settle in seconds and are irrevocable — and that combination created a crime that runs in minutes: authorized-push-payment fraud, where the victim is manipulated or coerced ("sequestro relâmpago") into sending the transfer themselves, and the money layers through 2–5 mule accounts before cashing out. Brazil measured what human-paced recovery achieves against that clock: the **MED** recovers **~7–14%** of stolen amounts depending on period and methodology — the BCB's **official 2025 figure is 7% of disputed value, with ~89% of refund requests denied**. **MED 2.0** (mandatory **Feb 2, 2026**) extends tracing to **five account layers** — institutional confirmation that recovery is a multi-hop tracing *and speed* problem, yet the loop still runs at human speed.

Colombia's **Bre-B** (live 2025, **200+ institutions**) launched with **no recovery mechanism at all**: disputes move at help-desk speed under SFC oversight, against a crime that moves at network speed. That asymmetry defines Reversa's two pilot markets — and its category: autonomous **recovery**, not prevention.

| | **Brazil / Pix** | **Colombia / Bre-B** |
|---|---|---|
| Recovery mechanism | MED (since 2021), MED 2.0 (mandatory Feb 2026, 5 account layers) | **None** |
| Measured recovery | ~7–14% (official 2025: **7% of disputed value**, ~89% of requests denied) | No standardized measurement |
| What Reversa is there | *The upgrade*: beat a mechanism that exists and underperforms | *The first mechanism*: greenfield |

→ Research: **[summary](docs/research.md)** · **[full investigation](docs/research-full.md)** (includes the global landscape of 100+ instant payment systems).

## Project Structure

```
reversa/
├── app/         # Core agent code
│   ├── agent.py               # Main agent logic
│   ├── agent_engine_app.py    # Agent Engine application logic
│   └── app_utils/             # App utilities and helpers
├── .github/                   # CI/CD pipeline configurations for GitHub Actions
├── deployment/                # Infrastructure and deployment scripts
├── notebooks/                 # Jupyter notebooks for prototyping and evaluation
├── tests/                     # Unit, integration, and load tests
├── GEMINI.md                  # AI-assisted development guide
├── Makefile                   # Development commands
└── pyproject.toml             # Project dependencies
```

> 💡 **Tip:** Use [Gemini CLI](https://github.com/google-gemini/gemini-cli) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)
- **Terraform**: For infrastructure deployment - [Install](https://developer.hashicorp.com/terraform/downloads)
- **make**: Build automation tool - [Install](https://www.gnu.org/software/make/) (pre-installed on most Unix-based systems)


## Quick Start

Install required packages and launch the local development environment:

```bash
make install && make playground
```

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install dependencies with pip (pyenv env `reversa`, Python 3.13)                            |
| `make playground`    | Launch local development environment                                                        |
| `make lint`          | Run code quality checks                                                                     |
| `make test`          | Run unit tests (no GCP needed)                                                              |
| `make test-integration` | Run integration tests (needs GCP project + Vertex auth)                                  |
| `make deploy`        | Deploy agent to Agent Engine                                                                |
| `make register-gemini-enterprise` | Register deployed agent to Gemini Enterprise                                  |
| `make inspector`     | Launch A2A Protocol Inspector (requires uv + npm; not converted to pip)                     |
| `make setup-dev-env` | Set up development environment resources using Terraform                                   |

For full command options and usage, refer to the [Makefile](Makefile).

## 🛠️ Project Management

| Command | What It Does |
|---------|--------------|
| `uvx agent-starter-pack setup-cicd` | One-command setup of entire CI/CD pipeline + infrastructure |
| `uvx agent-starter-pack upgrade` | Auto-upgrade to latest version while preserving customizations |
| `uvx agent-starter-pack extract` | Extract minimal, shareable version of your agent |

---

## Development

Edit your agent logic in `app/agent.py` and test with `make playground` - it auto-reloads on save.
Use notebooks in `notebooks/` for prototyping and Vertex AI Evaluation.
See the [development guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/development-guide) for the full workflow.

## Deployment

```bash
gcloud config set project <your-project-id>
make deploy
```
To set up your production infrastructure, run `uvx agent-starter-pack setup-cicd`.
See the [deployment guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/deployment) for details.

## Observability

Built-in telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.
See the [observability guide](https://googlecloudplatform.github.io/agent-starter-pack/guide/observability) for queries and dashboards.

## A2A Inspector

This agent supports the [A2A Protocol](https://a2a-protocol.org/). Use `make inspector` to test interoperability.
See the [A2A Inspector docs](https://github.com/a2aproject/a2a-inspector) for details.
