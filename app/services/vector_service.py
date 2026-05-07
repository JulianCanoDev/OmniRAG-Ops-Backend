from __future__ import annotations

import logging
from typing import Any

from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore
from langchain_core.vectorstores import VectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.indexes import SQLRecordManager, index
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 1000
_CHUNK_OVERLAP = 200


def _get_qdrant_client() -> QdrantClient:
    settings = get_settings()
    kwargs: dict[str, Any] = {"location": settings.qdrant_url}
    if settings.qdrant_api_key:
        kwargs["api_key"] = settings.qdrant_api_key
    return QdrantClient(**kwargs)


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    settings = get_settings()
    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.gemini_api_key,
    )


def _get_vector_store(
    client: QdrantClient | None = None,
) -> QdrantVectorStore:
    settings = get_settings()
    if client is None:
        client = _get_qdrant_client()
    return QdrantVectorStore(
        client=client,
        collection_name=settings.qdrant_collection,
        embedding=_get_embeddings(),
    )


def _ensure_collection_exists(client: QdrantClient) -> None:
    settings = get_settings()
    collections = client.get_collections().collections
    if not any(c.name == settings.qdrant_collection for c in collections):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(
                size=settings.vector_dimension,
                distance=models.Distance.COSINE,
            ),
        )
        logger.info("Created Qdrant collection '%s'", settings.qdrant_collection)


def _get_record_manager() -> SQLRecordManager:
    settings = get_settings()
    namespace = f"qdrant/{settings.qdrant_collection}"
    record_manager = SQLRecordManager(
        namespace=namespace, db_url="sqlite:///record_manager_cache.sql"
    )
    record_manager.create_schema()
    return record_manager


def index_documents(docs: list[Document]) -> dict[str, Any]:
    client = _get_qdrant_client()
    _ensure_collection_exists(client)
    vector_store = _get_vector_store(client)
    record_manager = _get_record_manager()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
    )
    split_docs = text_splitter.split_documents(docs)
    result = index(
        docs=split_docs,
        record_manager=record_manager,
        vector_store=vector_store,
        cleanup="incremental",
        source_id_key="source",
    )
    return {
        "status": result,
        "chunks_processed": len(split_docs),
    }


async def check_connectivity() -> tuple[bool, str]:
    try:
        client = _get_qdrant_client()
        client.get_collections()
        return True, "reachable"
    except Exception as exc:
        return False, str(exc)
