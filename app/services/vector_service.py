from __future__ import annotations

import logging
from typing import Any

from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.indexes import SQLRecordManager, index
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_CHUNK_SIZE = 1000
_CHUNK_OVERLAP = 200


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    settings = get_settings()
    return GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.GOOGLE_API_KEY,
    )


def _get_vector_store(client: QdrantClient) -> QdrantVectorStore:
    settings = get_settings()
    return QdrantVectorStore(
        client=client,
        collection_name=settings.COLLECTION_NAME,
        embedding=_get_embeddings(),
    )


def _ensure_collection_exists(client: QdrantClient) -> None:
    settings = get_settings()
    collections = client.get_collections().collections
    if not any(c.name == settings.COLLECTION_NAME for c in collections):
        client.create_collection(
            collection_name=settings.COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=768,
                distance=models.Distance.COSINE,
            ),
        )
        logger.info("Created Qdrant collection '%s'", settings.COLLECTION_NAME)


def _get_record_manager() -> SQLRecordManager:
    settings = get_settings()
    namespace = f"qdrant/{settings.COLLECTION_NAME}"
    record_manager = SQLRecordManager(
        namespace=namespace, db_url="sqlite:///record_manager.db"
    )
    record_manager.create_schema()
    return record_manager


def index_documents(
    docs: list[Document], client: QdrantClient
) -> dict[str, Any]:
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
        settings = get_settings()
        kwargs: dict[str, Any] = {"location": settings.QDRANT_URL}
        if settings.QDRANT_API_KEY:
            kwargs["api_key"] = settings.QDRANT_API_KEY
        client = QdrantClient(**kwargs)
        client.get_collections()
        return True, "reachable"
    except Exception as exc:
        return False, str(exc)
