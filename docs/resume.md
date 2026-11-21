# AapdaMitra — Resume Bullets

Three resume bullets framing the project end-to-end.

- Built **AapdaMitra**, a retrieval-augmented disaster-safety assistant for
  village families that answers flood, heatwave and earthquake questions from
  NDMA guidelines with cited retrieval, and abstains ("I don't know.") when the
  source data cannot support an answer instead of inventing safety advice.

- Engineered the pipeline end-to-end — HTML ingestion → chunking → MiniLM
  embeddings → Chroma vector store → FastAPI RAG service — plus a LangGraph
  agent with a human-in-the-loop approval step and a custom Rothfusz heat-index
  tool, fronted by a Streamlit chat UI with a printable **Before / During /
  After** checklist for the village notice board.

- Hardened the service for production: per-request latency and token logging,
  an answer cache that cuts repeat-question latency from ~1.4 s to under 1 ms,
  input-length limits, a prompt-injection guard, 39 pytest tests with
  ruff-clean CI, Docker Compose, and Render deployment.
