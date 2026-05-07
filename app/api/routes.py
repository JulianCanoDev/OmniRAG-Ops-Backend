from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.models.schemas import (
    IngestionRequest,
    IngestionResponse,
    HealthResponse,
    HealthComponent,
)
from app.services.ingestion import process_ingestion
from app.services.gemini_service import check_connectivity as check_gemini
from app.services.vector_service import check_connectivity as check_qdrant

logger = logging.getLogger(__name__)

router = APIRouter()

_SUPPORTED_EXTENSIONS: set[str] = {".pdf", ".docx", ".doc", ".xlsx", ".xls"}


@router.post(
    "/ingest",
    response_model=IngestionResponse,
    summary="Ingest text content into the vector store",
)
async def ingest_text(payload: IngestionRequest) -> IngestionResponse:
    return await process_ingestion(payload=payload)


@router.post(
    "/ingest/file",
    response_model=IngestionResponse,
    summary="Upload and ingest a PDF, Word, or Excel file",
)
async def ingest_file(file: UploadFile = File(...)) -> IngestionResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in _SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Accepted: {', '.join(sorted(_SUPPORTED_EXTENSIONS))}",
        )

    raw_bytes: bytes = await file.read()

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(raw_bytes)
        tmp_path = tmp.name

    return await process_ingestion(
        file_path=tmp_path, filename=file.filename
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check for all upstream services",
)
async def health() -> dict[str, Any]:
    gemini_ok, gemini_msg = await check_gemini()
    qdrant_ok, qdrant_msg = await check_qdrant()

    overall = "healthy" if gemini_ok and qdrant_ok else "degraded"

    return HealthResponse(
        status=overall,
        gemini=HealthComponent(
            status="ok" if gemini_ok else "unreachable", detail=gemini_msg
        ),
        qdrant=HealthComponent(
            status="ok" if qdrant_ok else "unreachable", detail=qdrant_msg
        ),
    ).model_dump()
