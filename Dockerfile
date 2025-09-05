FROM python:3.11-slim

RUN groupadd -r -g 1000 appuser && useradd -r -g appuser -u 1000 appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && apt-get autoremove -y

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

COPY src/ src/
COPY entrypoint.sh .

RUN mkdir -p /app/logs /tmp/fraud_bot_secure \
    && chown -R appuser:appuser /app \
    && chmod 700 /tmp/fraud_bot_secure \
    && chmod +x entrypoint.sh \
    && chmod 755 /app/logs

USER appuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app
ENV TMPDIR=/tmp/fraud_bot_secure

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys, os; sys.exit(0 if os.path.exists('/tmp/fraud_bot_secure') else 1)"

ENTRYPOINT ["./entrypoint.sh"]