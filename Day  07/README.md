# AapdaMitra

[![CI](https://github.com/KajalHonde/GenAI/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/KajalHonde/GenAI/actions/workflows/ci.yml)

## Deploy to Render

The repository root contains a Render Blueprint that creates separate API and
Streamlit UI services. In the Render Dashboard, create a Blueprint from this
repository and apply `render.yaml`. The API health check is `/health`; after
deployment, use the UI service URL for the public app.

Both services use Render's free plan. Its filesystem is ephemeral, so the
Chroma index is not durable across instance restarts. The embedding model is
downloaded when the API starts, which can make its first startup take longer.
To enable generated answers, configure `GROQ_API_KEY` on the API service in
Render's environment settings. Do not commit provider keys to the repository.

## Run with Docker

From this directory, start the FastAPI service and Streamlit UI with:

```bash
docker compose up --build
```

Open the UI at <http://localhost:8501>, the API at <http://localhost:8000>,
or its interactive docs at <http://localhost:8000/docs>. Docker Compose keeps
the Chroma index and UI feedback in named volumes.

The API starts without an LLM key, but answering questions requires a key for
the configured provider. Set `GROQ_API_KEY` (the default provider) or set
`LLM_PROVIDER=gemini` and provide `GEMINI_API_KEY` in the shell before running
Compose. The UI connects to the API service automatically.

Stop the services with `docker compose down`; add `-v` only if you also want
to remove the persisted Chroma index and feedback.

## Tests and lint

Install the development dependencies and run the test suite and Ruff from this
directory:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
ruff check .
```

## RAG Evaluation Results

| Configuration | Chunk Size | Top-K | Score | Q6 Abstention |
|---|---:|---:|---:|---|
| Config A | 100 | 3 | 9/15 (60.0%) | PASS |
| Config B | 150 | 5 | 9/15 (60.0%) | PASS |

**Winner:** Config A (Chunk Size: 100, Top-K: 3)
