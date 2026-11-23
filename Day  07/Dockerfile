FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    SENTENCE_TRANSFORMERS_HOME=/app/.model_cache \
    HF_HOME=/app/.model_cache

WORKDIR /app

# Install Python dependencies (cached layer).
COPY requirements-day7.txt .
RUN pip install --no-cache-dir -r requirements-day7.txt

# Copy application code.
COPY . .

# Pre-download the embedding model at build time so there is no
# network download at runtime — avoids Render's health-check timeout.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2'); print('Model cached OK')"

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
