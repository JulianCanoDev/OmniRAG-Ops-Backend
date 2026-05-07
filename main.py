from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
)

app = FastAPI(
    title="OmniRAG-Ops",
    description="High-performance RAG Ingestion Engine — ingest, query, manage, and monitor documents with Gemini metadata enrichment and Qdrant vector storage",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup() -> None:
    settings = get_settings()
    logger.info("OmniRAG-Ops startup complete — multi-format ingestion ready")
    logger.info(
        "Stateless Middleware — connecting to remote vector database at %s",
        settings.QDRANT_URL,
    )
    logger.info(
        "QDRANT_API_KEY is %s — operating in %s mode",
        "set" if settings.QDRANT_API_KEY else "not set",
        "authenticated (cloud/managed)" if settings.QDRANT_API_KEY else "unauthenticated (trusted network)",
    )


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        log_level=settings.LOG_LEVEL,
        reload=False,
    )


if __name__ == "__main__":
    main()
