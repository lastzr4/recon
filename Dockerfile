FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps required by pdfplumber (via pillow/pdfminer) for image handling.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libjpeg62-turbo-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f "http://localhost:${PORT:-8080}/_stcore/health" || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]

# Note: Railway's "startCommand" (railway.json) takes precedence over this
# CMD and is always executed through a shell, so it can safely use
# `sh -c "..."` with $PORT expansion there. This CMD is only a fallback used
# when no startCommand override is set, so it intentionally avoids any
# ${PORT} shell-expansion syntax (which would otherwise be passed to
# Streamlit as a literal, unparsed string) and binds to a fixed default
# port instead.
