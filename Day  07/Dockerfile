FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    # Tell sentence-transformers where to cache the model so it stays
    # in the image layer and does not need to be re-downloaded at runtime.
    SENTENCE_TRANSFORMERS_HOME=/app/.model_cache \
    HF_HOME=/app/.model_cache

WORKDIR /app

# Install Python dependencies first (cached layer).
COPY requirements-day7.txt .
RUN pip install --no-cache-dir -r requirements-day7.txt

# Copy application code.
COPY . .

# Pre-download the embedding model at build time so the runtime container
# starts immediately without a 90 MB download — critical on Render free tier.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Pre-build the ChromaDB index from the bundled NDMA documents so the
# /health and /search/semantic endpoints work from the first request
# without a separate indexing step.
RUN python -m app.index_documents

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
