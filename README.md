# ZonaAi

ZONA AI is a privacy-first, modular, hybrid (offline/online) AI runtime with memory, token economy, and self-healing infrastructure.

## Project Structure

```
ZonaAi/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── kernel/zona_kernel.py   # Obfuscation, OpenAI API wrapper
│   └── static/                 # Minimal browser chat interface
├── Dockerfile
├── requirements.txt
├── cloudbuild.yaml             # Alternative GCP deploy script
└── .github/
    └── workflows/
        └── deploy.yml          # GitHub Actions workflow for Cloud Run
```

## Local Development

Copy `.env.template` to `.env` and populate it with your keys and preferences:

```bash
cp .env.template .env
```

Key variables include:

- `OPENAI_API_KEY`, `GEMINI_API_KEY` – provider API keys
- `LICENSE_KEY` – enables premium providers such as Gemini and Vertex AI
- `USE_FIRESTORE` / `FIRESTORE_PROJECT_ID` – store chat memory in Firestore
- `DATABASE_URL` – use SQLite/Postgres for persistent memory storage
- `DEFAULT_PROVIDER` – default provider for `/prompt` requests

Run the app locally with:

```bash
uvicorn app.main:app --reload --port 8000
```

Then visit `http://localhost:8000` in your browser to use the built‑in chat UI.

## Providers

The `/prompt` endpoint requires a `provider` field to select which LLM backend to use. Available providers are:

- `openai` – set `OPENAI_API_KEY` to your API key; uses OpenAI's ChatCompletion API.
- `vertexai` – uses Google Cloud Vertex AI; requires a valid license and `FIRESTORE_PROJECT_ID`.

Example request body:

```json
{
  "prompt": "Hello",
  "provider": "openai"
}
```

Additional providers can be registered at runtime using `ZonaKernel.add_provider`.

## Plugins

Zona includes a lightweight plugin system. Plugins can expose a simple
`run` function or subclass `PluginBase` for a more structured interface with
metadata and contextual arguments. Example plugins live in `zona/plugins/`.

## Docker

```bash
docker build -t zona-api .
docker run -p 8080:8080 zona-api
```

## Deployment

On pushes to `main`, `.github/workflows/deploy.yml` deploys the service to Google Cloud Run. Ensure the following secrets are configured:

- `GCP_PROJECT_ID`
- `GCP_SA_KEY`

Alternatively, use Cloud Build with `cloudbuild.yaml`.

## Logging

Zona logs each interaction to standard output. Each entry includes the session ID, the prompt, and the response handled by `log_interaction` in `app/utils/logger.py`.
