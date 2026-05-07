# ---------------------------------------------------------------
# Stage 1 — builder
# ---------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        --prefix=/install \
        -r requirements.txt

# ---------------------------------------------------------------
# Stage 2 — runtime (non-root)
# ---------------------------------------------------------------
FROM python:3.11-slim AS runtime

RUN groupadd --gid 10001 app && \
    useradd --uid 10001 --gid app --create-home app

COPY --from=builder /install /usr/local

WORKDIR /app

COPY --chown=app:app . .

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python", "main.py"]
