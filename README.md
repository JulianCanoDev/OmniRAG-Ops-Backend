# OmniRAG-Ops

**High-performance RAG Ingestion Engine** with AI-powered metadata enrichment.

---

## Architecture

```
Client ──► FastAPI ──► Gemini (metadata enrichment)
                │
                └────► Qdrant (vector store, dedup via RecordManager)
```

### Key components

| Layer       | Technology              | Role                                    |
|-------------|-------------------------|-----------------------------------------|
| API         | FastAPI + Uvicorn       | HTTP interface for ingestion & health   |
| AI          | Gemini 2.5 Flash        | Summarisation, category & priority tags |
| Vector DB   | Qdrant                  | Store & retrieve embeddings             |
| Indexing    | LangChain Indexing API  | Dedup content via SQLRecordManager      |
| Embeddings  | Google text-embedding-004 | Generate vector representations       |

### How ingestion works

1. Content is received via `/api/v1/ingest` (text) or `/api/v1/ingest/file` (PDF).
2. Content is sent to **Gemini 2.5 Flash** for metadata enrichment (summary, category, priority).
3. Content is split into chunks using `RecursiveCharacterTextSplitter`.
4. Chunks are indexed into **Qdrant** using LangChain's `index()` API, which leverages a **SQLRecordManager** to skip duplicates by source ID.
5. A response is returned with the document ID and enriched metadata.

---

## Quick start

### Prerequisites

- Python 3.11+
- A running Qdrant instance (or Qdrant Cloud)
- A Google Gemini API key

### Environment variables

| Variable             | Default                  | Required |
|----------------------|--------------------------|----------|
| `GEMINI_API_KEY`     | —                        | Yes      |
| `GEMINI_MODEL`       | `gemini-2.5-flash`       | No       |
| `QDRANT_URL`         | `http://localhost:6333`  | No       |
| `QDRANT_API_KEY`     | —                        | No       |
| `QDRANT_COLLECTION`  | `omnirarg_docs`          | No       |
| `APP_HOST`           | `0.0.0.0`                | No       |
| `APP_PORT`           | `8000`                   | No       |

### Run with Docker

```bash
docker build -t omnirarg-ops .
docker run -d \
  -p 8000:8000 \
  -e GEMINI_API_KEY="your-key" \
  -e QDRANT_URL="http://host.docker.internal:6333" \
  omnirarg-ops
```

### Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GEMINI_API_KEY="your-key"
python main.py
```

---

## API reference

### `POST /api/v1/ingest`

Ingest raw text.

```json
{
  "content": "Your document text here...",
  "source": "my-doc.txt"
}
```

### `POST /api/v1/ingest/file`

Upload a PDF file (multipart/form-data, field name: `file`).

### `GET /api/v1/health`

Returns connectivity status for Gemini and Qdrant.

```json
{
  "status": "healthy",
  "timestamp": "2026-01-01T00:00:00Z",
  "gemini": { "status": "ok", "detail": "reachable" },
  "qdrant": { "status": "ok", "detail": "reachable" }
}
```

---

## Project structure

```
OmniRAG-Ops/
├── main.py                  # Entry point
├── requirements.txt
├── Dockerfile
├── README.md
└── app/
    ├── __init__.py
    ├── api/
    │   ├── __init__.py
    │   └── routes.py        # Endpoint definitions
    ├── core/
    │   ├── __init__.py
    │   └── config.py        # Settings & environment
    ├── models/
    │   ├── __init__.py
    │   └── schemas.py       # Pydantic models
    └── services/
        ├── __init__.py
        ├── gemini_service.py    # Gemini LLM integration
        ├── vector_service.py    # Qdrant + embedding logic
        └── ingestion_service.py # Orchestrator
```

---

## Development

```bash
# Install dev extras
pip install ruff pytest httpx

# Lint
ruff check .

# Run tests (add your own under tests/)
pytest -v
```

---

## License

MIT
