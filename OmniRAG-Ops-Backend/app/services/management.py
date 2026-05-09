from __future__ import annotations

import logging
from typing import Any

from langchain_core.documents import Document

from app.models.schemas import (
    DocumentResponse,
    DocumentListResponse,
    QueryResponse,
    QueryResult,
    StatsResponse,
)
from app.services.vector_service import (
    get_qdrant_client,
    delete_by_source,
    search_similar,
    scroll_points_paginated,
    scroll_all_points,
    update_payload_by_source,
)

logger = logging.getLogger(__name__)


def _payload_to_document(payload: dict[str, Any]) -> DocumentResponse | None:
    doc_id = payload.get("document_id")
    if not doc_id:
        return None
    return DocumentResponse(
        document_id=str(doc_id),
        source=str(payload.get("source", "")),
        summary=str(payload.get("summary", "")),
        category=str(payload.get("category", "")),
        priority=str(payload.get("priority", "")),
    )


def list_documents(skip: int, limit: int) -> DocumentListResponse:
    client = get_qdrant_client()
    docs_map: dict[str, DocumentResponse] = {}
    total_scanned = 0

    while True:
        batch, _ = scroll_points_paginated(client, limit=1000, offset=total_scanned)
        if not batch:
            break
        for point in batch:
            total_scanned += 1
            if point.payload is None:
                continue
            doc_id = point.payload.get("document_id")
            if not doc_id:
                continue
            doc_id_str = str(doc_id)
            if doc_id_str in docs_map:
                docs_map[doc_id_str].chunk_count += 1
            else:
                doc = _payload_to_document(point.payload)
                if doc is not None:
                    doc.chunk_count = 1
                    docs_map[doc_id_str] = doc

    sorted_docs = list(docs_map.values())
    total = len(sorted_docs)
    paginated = sorted_docs[skip : skip + limit]

    return DocumentListResponse(
        total=total, skip=skip, limit=limit, items=paginated
    )


def get_document(doc_id: str) -> DocumentResponse | None:
    client = get_qdrant_client()
    batch, _ = scroll_points_paginated(client, limit=10000)
    for point in batch:
        if point.payload and str(point.payload.get("document_id", "")) == doc_id:
            chunk_count = sum(
                1
                for p in batch
                if p.payload and str(p.payload.get("document_id", "")) == doc_id
            )
            doc = _payload_to_document(point.payload)
            if doc is not None:
                doc.chunk_count = chunk_count
                return doc
    return None


def delete_document(source_id: str) -> int:
    client = get_qdrant_client()
    return delete_by_source(source_id, client)


def query_documents(question: str, top_k: int) -> QueryResponse:
    client = get_qdrant_client()
    results: list[tuple[Document, float]] = search_similar(question, top_k, client)
    items = [
        QueryResult(
            chunk_content=doc.page_content,
            score=score,
            metadata=doc.metadata,
        )
        for doc, score in results
    ]
    return QueryResponse(results=items)


def get_statistics() -> StatsResponse:
    client = get_qdrant_client()
    points = scroll_all_points(client)

    doc_ids: set[str] = set()
    category_counts: dict[str, int] = {}
    priority_counts: dict[str, int] = {}

    for point in points:
        if point.payload is None:
            continue
        doc_id = str(point.payload.get("document_id", ""))
        if doc_id:
            doc_ids.add(doc_id)

        cat = str(point.payload.get("category", "unknown"))
        category_counts[cat] = category_counts.get(cat, 0) + 1

        pri = str(point.payload.get("priority", "unknown"))
        priority_counts[pri] = priority_counts.get(pri, 0) + 1

    total_docs = len(doc_ids)

    return StatsResponse(
        total_documents=total_docs,
        total_chunks=len(points),
        category_distribution=dict(
            sorted(category_counts.items(), key=lambda x: -x[1])
        ),
        priority_distribution=dict(
            sorted(priority_counts.items(), key=lambda x: -x[1])
        ),
    )


def update_document_metadata(
    source_id: str, updates: dict[str, Any]
) -> int:
    client = get_qdrant_client()
    filtered = {k: v for k, v in updates.items() if v is not None}
    if not filtered:
        return 0
    return update_payload_by_source(source_id, filtered, client)
