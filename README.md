# OmniRAG-Ops

**Production-grade RAG Operations platform** — a full-stack monorepo with a FastAPI ingestion engine and a Next.js management dashboard.

```
Omni-RAG/
├── OmniRAG-Ops-Backend/     # FastAPI ingestion engine
└── OmniRAG-Ops-Frontend/    # Next.js management dashboard
```

---

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │           OmniRAG-Ops-Frontend           │
                    │       Next.js 15 + TanStack Query        │
                    └────────────────┬────────────────────────┘
                                     │ JWT Bearer
                    ┌────────────────▼────────────────────────┐
                    │           OmniRAG-Ops-Backend            │
                    │        FastAPI + Gemini + Qdrant          │
                    │                                          │
                    ├──► Qdrant (vector store)                  │
                    ├──► PostgreSQL (users + dedup)             │
                    └──────────────────────────────────────────┘
```

## Repositories

| Component | Directory | Stack |
|-----------|-----------|-------|
| **Backend** | `OmniRAG-Ops-Backend/` | Python, FastAPI, Gemini, Qdrant, PostgreSQL |
| **Frontend** | `OmniRAG-Ops-Frontend/` | Next.js 15, TypeScript, Tailwind CSS, Shadcn/UI |

## Quick start

### Backend

```bash
cd OmniRAG-Ops-Backend
cp .env.example .env
# Edit .env — set GOOGLE_API_KEY, QDRANT_URL, QDRANT_API_KEY, SECRET_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Frontend

```bash
cd OmniRAG-Ops-Frontend
cp .env.example .env.local
# Edit .env.local — set NEXT_PUBLIC_API_URL
npm install
npm run dev
```

### Docker Compose

```bash
cd OmniRAG-Ops-Backend
docker compose up -d
```

---

## License

MIT
