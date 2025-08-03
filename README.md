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

```bash
export OPENAI_API_KEY=sk-...
uvicorn app.main:app --reload --port 8000
```

Then visit `http://localhost:8000` in your browser to use the built‑in chat UI.

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
