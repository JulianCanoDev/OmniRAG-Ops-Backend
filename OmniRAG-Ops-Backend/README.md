# OmniRAG-Ops

**Production-grade RAG Ingestion Engine** — stateless middleware that ingests documents, enriches metadata via Gemini AI, stores vectors in remote Qdrant, and manages deduplication via PostgreSQL. Secured with JWT authentication.

```
                         ┌──────────────────────────────────────────────────────────┐
                         │                  OmniRAG-Ops (stateless)                 │
                         │                                                          │
 Client ──► JWT Auth ──► FastAPI ──► Gemini 2.5 Flash (metadata enrichment)         │
                         │                                                          │
                         ├──► Qdrant Client (remote, url+api_key)                   │
                         │     ├── Data plane: ingest, query, search                │
                         │     └── Control plane: create / delete / list collections│
                         │                                                          │
                         ├──► PostgreSQL (RecordManager dedup + User auth store)    │
                         └──────────────────────────────────────────────────────────┘
```

Zero local storage — all data resides in external Qdrant and PostgreSQL. Designed for Dokploy / Docker Compose deployment.

---

## Features

- **Multi-format ingestion** — PDF, Word (DOCX/DOC), Excel (XLSX/XLS), images (PNG/JPG), raw text
- **AI metadata enrichment** — Gemini 2.5 Flash generates summary, category, and priority tags
- **JWT authentication** — Register / login flow, protected ingestion & collection endpoints
- **PostgreSQL-backed dedup** — LangChain `SQLRecordManager` skips duplicate chunks on re-ingest
- **Remote Qdrant control plane** — Create, list, and delete collections programmatically
- **Connection pooling** — SQLAlchemy engine with `pool_size=5`, `max_overflow=10`
- **Stateless by design** — no local vector DB, no local file storage
- **Production logging** — `[Stateless Middleware]` identity tag in every log line
- **Docker Compose** — API + PostgreSQL, DNS overrides, healthchecks, log rotation

---

## Quick start

### Prerequisites

| Dependency | Notes |
|------------|-------|
| [Qdrant](https://qdrant.tech/documentation/quick-start/) | Cloud or self-hosted |
| [Google Gemini API key](https://aistudio.google.com/apikey) | For embeddings & enrichment |

### Local development

```bash
git clone https://github.com/JulianCanoDev/OmniRAG-Ops-Backend && cd OmniRAG-Ops

cp .env.example .env
# Edit .env — set GOOGLE_API_KEY, QDRANT_URL, QDRANT_API_KEY, SECRET_KEY

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Docker Compose (recommended for production)

```bash
docker compose up -d
```

This starts:
- `omnirg-api` — the FastAPI application (port 8000)
- `omnirg-db` — PostgreSQL 16 (RecordManager + user storage)

Both services include healthchecks, restart policies, DNS overrides (`8.8.8.8`, `1.1.1.1`), and log rotation.

---

## Authentication

All protected endpoints require a Bearer JWT token in the `Authorization` header.

### `POST /api/v1/auth/register`

```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

```json
// HTTP 201
{
  "id": "a1b2c3d4-...",
  "email": "user@example.com",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-01-01T00:00:00Z"
}
```

### `POST /api/v1/auth/login`

Send as `application/x-www-form-urlencoded` with fields `username` and `password`.

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

Use the token in subsequent requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## Environment variables

| Variable | Default | Required | Description |
|---|---|---|---|
| `GOOGLE_API_KEY` | — | Yes | Gemini API key |
| `QDRANT_URL` | `http://localhost:6333` | No | Remote Qdrant URL |
| `QDRANT_API_KEY` | — | No | Qdrant Cloud API key |
| `COLLECTION_NAME` | `omnirarg_docs` | No | Default Qdrant collection |
| `GEMINI_MODEL` | `gemini-2.5-flash` | No | Gemini model for enrichment |
| `EMBEDDING_MODEL_ID` | `models/gemini-embedding-2` | No | Embedding model |
| `EMBEDDING_OUTPUT_DIMENSIONALITY` | `1536` | No | Matryoshka output dim (256–3072) |
| `HOST` | `0.0.0.0` | No | Uvicorn bind address |
| `PORT` | `8000` | No | Uvicorn port |
| `LOG_LEVEL` | `info` | No | Uvicorn log level |
| `DATABASE_URL` | `postgresql+psycopg2://omnirg:omnirg@db:5432/omnirg` | No | PostgreSQL connection string |
| `RECORD_MANAGER_NAMESPACE` | `omnirag/upsert_records` | No | SQLRecordManager namespace |
| `SECRET_KEY` | `change-me-in-production` | **Yes** | JWT signing key |
| `ALGORITHM` | `HS256` | No | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | No | Token TTL |
| `CHUNK_SIZE` | `1000` | No | Text splitter chunk size |
| `CHUNK_OVERLAP` | `200` | No | Text splitter overlap |

All settings loaded via **pydantic-settings** (`app/core/config.py`).

---

## API reference

Protected endpoints require `Authorization: Bearer <token>`.

### Ingestion (🔒 Protected)

#### `POST /api/v1/ingest`

Ingest raw text.

```json
{ "content": "Your document text...", "source": "my-doc.txt" }
```

#### `POST /api/v1/ingest/file` — `multipart/form-data`

Upload a file (`field: file`).

| Format  | Extensions |
|---|---|
| PDF | `.pdf` |
| Word | `.docx`, `.doc` |
| Excel | `.xlsx`, `.xls` |
| Image | `.png`, `.jpg`, `.jpeg` |

```json
{
  "status": "success",
  "document_id": "uuid",
  "chunks_processed": 12,
  "metadata": { "summary": "...", "category": "tech", "priority": "high" },
  "message": "Document ingested successfully"
}
```

### Document Management (Public)

#### `GET /api/v1/documents?skip=0&limit=20`

List documents with pagination.

#### `GET /api/v1/documents/{doc_id}`

Get document by UUID.

#### `DELETE /api/v1/documents/{source_id}`

Deep delete by source (filename). Removes from Qdrant + RecordManager.

```json
{ "status": "deleted", "source_id": "report.pdf", "points_removed": 12 }
```

#### `PATCH /api/v1/documents/{source_id}/metadata`

Override Gemini-generated metadata.

```json
{ "category": "legal", "priority": "high" }
```

### Search (Public)

#### `POST /api/v1/query`

```json
{ "question": "What were the Q3 earnings?", "top_k": 5 }
```

```json
{
  "results": [
    { "chunk_content": "Revenue up 15%...", "score": 0.89, "metadata": { ... } }
  ]
}
```

### Statistics (Public)

#### `GET /api/v1/stats`

```json
{
  "total_documents": 42,
  "total_chunks": 312,
  "category_distribution": { "finance": 18, "technology": 14, "healthcare": 7, "unknown": 3 },
  "priority_distribution": { "medium": 20, "high": 12, "low": 10 }
}
```

### Health (Public)

#### `GET /api/v1/health`

Returns **200** if Gemini + Qdrant are reachable, **503** otherwise.

```json
{ "status": "healthy", "gemini": { "status": "ok" }, "qdrant": { "status": "ok" } }
```

### Collection Control Plane (🔒 Protected)

#### `POST /api/v1/collections`

```json
{ "name": "my_collection", "vector_size": 1536, "distance": "Cosine" }
```

Returns **201** or **409** (conflict).

#### `DELETE /api/v1/collections/{name}`

Returns **200** or **404**.

#### `GET /api/v1/collections`

```json
{
  "collections": [
    { "name": "omnirarg_docs", "status": "green", "vectors_count": 312 }
  ]
}
```

---

## Project structure

```
OmniRAG-Ops/
├── docker-compose.yml       # API + PostgreSQL services
├── Dockerfile               # python:3.13-slim multi-stage build
├── main.py                  # FastAPI entry point
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── app/
    ├── api/
    │   ├── __init__.py
    │   ├── auth.py           # /auth/register, /auth/login
    │   └── routes.py         # All other endpoints
    ├── core/
    │   ├── __init__.py
    │   ├── config.py         # pydantic-settings (all env vars)
    │   └── security.py       # Password hashing, JWT, get_current_user
    ├── models/
    │   ├── __init__.py
    │   ├── schemas.py        # Pydantic request/response models
    │   └── user.py           # SQLAlchemy User model + auth schemas
    └── services/
        ├── __init__.py
        ├── collection_service.py  # Qdrant collection CRUD
        ├── gemini_service.py      # Gemini LLM integration
        ├── ingestion.py           # Document loading + orchestration + shared DB engine
        ├── management.py          # Query, stats, CRUD business logic
        └── vector_service.py      # Qdrant vector store, indexing, RecordManager
```

---

## Development

```bash
pip install ruff pytest httpx
ruff check .
pytest -v
```

---

## Repository safety

The `.gitignore` blocks:

- `.env` — secrets and credentials
- `__pycache__/`, `.venv/`, IDE files, OS artefacts

Always copy `.env.example` to `.env` and fill in your real values — never commit `.env`.

---

## License

MIT — see [LICENSE](LICENSE).
