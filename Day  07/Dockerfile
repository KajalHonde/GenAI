FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app

# Install dependencies — onnxruntime (~50 MB) instead of torch (~2 GB)
# so the image fits inside Render's free-tier memory limit (512 MB).
COPY requirements-day7.txt .
RUN pip install --no-cache-dir -r requirements-day7.txt

COPY . .

# Warm-up: download the ONNX MiniLM model at build time so runtime
# cold-starts don't need a network download.
RUN python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()([ 'warm up']); print('ONNX model cached OK')"

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
