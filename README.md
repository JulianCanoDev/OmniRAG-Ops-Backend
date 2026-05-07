# OmniRAG-Ops

**High-performance RAG Ingestion Engine** with AI-powered metadata enrichment. Supports PDF, Word, Excel, and raw text.

---

## Architecture

```
Client ──► FastAPI ──► Gemini (metadata enrichment)
                │
                └────► Qdrant (vector store, dedup via RecordManager)
```

### Key components

| Layer             | Technology                  | Role                                      |
|-------------------|-----------------------------|-------------------------------------------|
| API               | FastAPI + Uvicorn           | HTTP interface for ingestion & health     |
| AI                | Gemini 2.5 Flash            | Summarisation, category & priority tags   |
| Vector DB         | Qdrant (external)           | Store & retrieve embeddings               |
| Indexing          | LangChain Indexing API      | Dedup content via SQLRecordManager        |
| Embeddings        | Google text-embedding-004   | Generate vector representations           |
| Document Loaders  | LangChain Community Loaders | Parse PDF, DOCX, XLSX into text           |
| Config            | pydantic-settings           | Load env vars from `.env` file            |

### Supported file formats

| Format    | Extension(s)  | Loader                | Library       |
|-----------|---------------|-----------------------|---------------|
| PDF       | `.pdf`        | `PyPDFLoader`         | pypdf         |
| Word      | `.docx`, `.doc` | `Docx2txtLoader`    | python-docx   |
| Excel     | `.xlsx`, `.xls` | `_ExcelLoader` (custom, pandas-backed) | pandas + openpyxl |
| Text      | —             | Inline ingestion      | —             |

### How ingestion works

1. Content is received via `/api/v1/ingest` (raw text) or `/api/v1/ingest/file` (PDF / Word / Excel).
2. The route saves the uploaded file to a **temporary directory** (`tempfile.NamedTemporaryFile`) and passes the path to `ingestion.py`.
3. `_get_loader(file_path, extension)` dispatches to the correct LangChain document loader (`PyPDFLoader`, `Docx2txtLoader`, or `_ExcelLoader`).
4. A **Qdrant client** is created in `app/services/ingestion.py` — it connects to an externally-running Qdrant instance (no embedded DB).
5. Extracted text is sent to **Gemini 2.5 Flash** for metadata enrichment (summary, category, priority).
6. Enriched metadata (document_id, source, summary, category, priority) is attached to every chunk.
7. Content is split into chunks using `RecursiveCharacterTextSplitter`.
8. Chunks are indexed into **Qdrant** using LangChain's `index()` API, which leverages a **SQLRecordManager** (backed by local SQLite `record_manager.db`) to skip duplicates by source ID.
9. A response is returned with the document ID, chunk count, and enriched metadata.

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

Upload a file. Supported formats:

| Format  | Extensions                |
|---------|---------------------------|
| PDF     | `.pdf`                    |
| Word    | `.docx`, `.doc`           |
| Excel   | `.xlsx`, `.xls`           |

Send as `multipart/form-data` with field name `file`.

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
        ├── ingestion.py         # _get_loader + Qdrant client + orchestration
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
