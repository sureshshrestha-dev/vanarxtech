FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and source files
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY main.py eval_suite.py create_sample_pdf.py ./

# Install python packages
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    pypdf \
    openai \
    numpy \
    rank-bm25 \
    python-dotenv \
    pydantic \
    httpx \
    qdrant-client

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
