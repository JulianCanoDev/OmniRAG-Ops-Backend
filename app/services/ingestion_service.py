from __future__ import annotations

import logging
import uuid
from typing import Any

from langchain_core.documents import Document

from app.models.schemas import IngestionRequest, IngestionResponse
from app.services.gemini_service import enrich_metadata
from app.services.vector_service import index_documents

logger = logging.getLogger(__name__)


def _parse_pdf(raw_bytes: bytes) -> str:
    from io import BytesIO
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(raw_bytes))
    pages = [page.extract_text() for page in reader.pages if page.extract_text()]
    return "\n\n".join(pages)


async def process_ingestion(
    payload: IngestionRequest | None = None,
    file_bytes: bytes | None = None,
    filename: str | None = None,
) -> IngestionResponse:
    if payload is not None:
        content = payload.content
        source = payload.source
    elif file_bytes is not None:
        content = _parse_pdf(file_bytes)
        source = filename or "uploaded.pdf"
    else:
        return IngestionResponse(
            status="error", message="No content or file provided"
        )

    metadata_enrichment = await enrich_metadata(content)

    doc_id = str(uuid.uuid4())
    doc = Document(
        page_content=content,
        metadata={
            "document_id": doc_id,
            "source": source,
            "summary": metadata_enrichment.summary,
            "category": metadata_enrichment.category,
            "priority": metadata_enrichment.priority,
        },
    )

    index_result: dict[str, Any] = index_documents([doc])

    return IngestionResponse(
        status="success",
        document_id=doc_id,
        chunks_processed=index_result.get("chunks_processed", 0),
        metadata={
            "summary": metadata_enrichment.summary,
            "category": metadata_enrichment.category,
            "priority": metadata_enrichment.priority,
        },
        message="Document ingested successfully",
    )
