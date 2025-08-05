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

## Setup

1. **Create an environment file**

   Copy the provided template and fill in your API keys and preferences:

   ```bash
   cp .env.template .env
   ```

   Key variables include:

   - `OPENAI_API_KEY`, `GEMINI_API_KEY` – provider API keys
   - `LICENSE_KEY` – enables premium providers such as Gemini and Vertex AI
   - `USE_FIRESTORE` / `FIRESTORE_PROJECT_ID` – store chat memory in Firestore
   - `DATABASE_URL` – use SQLite/Postgres for persistent memory storage
   - `DEFAULT_PROVIDER` – default provider for `/prompt` requests

2. **Run locally**

   Install dependencies and start the development server:

   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

   Visit `http://localhost:8000` in your browser to use the built‑in chat UI.

3. **Run with Docker**

   Build and run the container, passing in your `.env` file:

   ```bash
   docker build -t zona-api .
   docker run --env-file .env -p 8080:8080 zona-api
   ```

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

## Integrations

Zona includes an experimental integration engine for connecting to external
systems such as accounting or CRM platforms. Available connectors can be listed
via `GET /integrations/available`. New integrations may be added with
`POST /integrations/add`, while `GET /integrations/scan` performs a best-effort
discovery of resources in the configured cloud project.

## Plugins

Zona includes a lightweight plugin system. Plugins can expose a simple
`run` function or subclass `PluginBase` for a more structured interface with
metadata and contextual arguments. Example plugins live in `zona/plugins/`.

## Deployment

On pushes to `main`, `.github/workflows/deploy.yml` deploys the service to Google Cloud Run. Ensure the following secrets are configured:

- `GCP_PROJECT_ID`
- `GCP_SA_KEY`

Alternatively, use Cloud Build with `cloudbuild.yaml`.

## Logging

Zona logs each interaction to standard output. Each entry includes the session ID, the prompt, and the response handled by `log_interaction` in `app/utils/logger.py`.

## Privacy
For details on what user data is collected, how it is stored, retention periods, deletion procedures, and GDPR rights, see [PRIVACY.md](PRIVACY.md).
