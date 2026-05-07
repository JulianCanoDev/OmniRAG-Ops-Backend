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

| Layer       | Technology                | Role                                    |
|-------------|---------------------------|-----------------------------------------|
| API         | FastAPI + Uvicorn         | HTTP interface for ingestion & health   |
| AI          | Gemini 2.5 Flash          | Summarisation, category & priority tags |
| Vector DB   | Qdrant (external)         | Store & retrieve embeddings             |
| Indexing    | LangChain Indexing API    | Dedup content via SQLRecordManager      |
| Embeddings  | Google text-embedding-004 | Generate vector representations         |
| Config      | pydantic-settings         | Load env vars from `.env` file          |

### How ingestion works

1. Content is received via `/api/v1/ingest` (text) or `/api/v1/ingest/file` (PDF).
2. A **Qdrant client** is created in `app/services/ingestion.py` — it connects to an externally-running Qdrant instance (no embedded DB).
3. Content is sent to **Gemini 2.5 Flash** for metadata enrichment (summary, category, priority).
4. Content is split into chunks using `RecursiveCharacterTextSplitter`.
5. Chunks are indexed into **Qdrant** using LangChain's `index()` API, which leverages a **SQLRecordManager** (backed by local SQLite `record_manager.db`) to skip duplicates by source ID.
6. A response is returned with the document ID and enriched metadata.

---

## Quick start

### Prerequisites

- Python 3.11+
- A running Qdrant instance ([Docker](https://qdrant.tech/documentation/quick-start/) or [Qdrant Cloud](https://cloud.qdrant.io/))
- A Google Gemini API key

### Setup

```bash
# 1. Clone and enter the project
git clone <repo-url> && cd OmniRAG-Ops

# 2. Configure environment
cp .env.example .env
# Edit .env with your actual keys

# 3. Install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. Run
python main.py
```

### Environment variables

| Variable           | Default                  | Required | Description                           |
|--------------------|--------------------------|----------|---------------------------------------|
| `GOOGLE_API_KEY`   | —                        | Yes      | Gemini API key                        |
| `QDRANT_URL`       | `http://localhost:6333`  | No       | Qdrant server URL                     |
| `QDRANT_API_KEY`   | —                        | No       | Qdrant API key (if using Cloud)       |
| `COLLECTION_NAME`  | `omnirarg_docs`          | No       | Qdrant collection name                |
| `GEMINI_MODEL`     | `gemini-2.5-flash`       | No       | Gemini model ID                       |
| `APP_HOST`         | `0.0.0.0`                | No       | FastAPI bind address                  |
| `APP_PORT`         | `8000`                   | No       | FastAPI port                          |
| `LOG_LEVEL`        | `info`                   | No       | Logging level                         |

Settings are managed via **pydantic-settings** (`app/core/config.py`) which reads from a `.env` file at the project root. A template is provided at `.env.example`.

### Run with Docker

```bash
docker build -t omnirarg-ops .
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_API_KEY="your-key" \
  -e QDRANT_URL="http://host.docker.internal:6333" \
  omnirarg-ops
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
├── .env.example             # Environment variable template
├── .gitignore
├── README.md
└── app/
    ├── __init__.py
    ├── api/
    │   ├── __init__.py
    │   └── routes.py        # Endpoint definitions
    ├── core/
    │   ├── __init__.py
    │   └── config.py        # pydantic-settings BaseSettings
    ├── models/
    │   ├── __init__.py
    │   └── schemas.py       # Pydantic models
    └── services/
        ├── __init__.py
        ├── ingestion.py         # Qdrant client init + orchestration
        ├── gemini_service.py    # Gemini LLM integration
        └── vector_service.py    # Qdrant vector store + indexing
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

## Repository safety

The `.gitignore` blocks the following from being committed:

- `.env` — secrets and credentials
- `record_manager.db` / `*.db` / `*.sqlite` — local RecordManager cache
- `__pycache__/`, `.venv/`, IDE files, and OS artefacts

Always copy `.env.example` to `.env` and fill in your real values — never commit the `.env` file.

---

## License

MIT
