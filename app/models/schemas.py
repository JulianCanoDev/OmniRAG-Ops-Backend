from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class IngestionRequest(BaseModel):
    content: str = Field(
        ..., min_length=1, description="Raw text content to ingest"
    )
    source: str = Field(
        default="manual",
        description="Origin identifier for the content (e.g. filename, URL)",
    )


class IngestionResponse(BaseModel):
    status: str
    document_id: str | None = None
    chunks_processed: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    message: str = ""


class MetadataEnrichment(BaseModel):
    summary: str = Field(..., description="Gemini-generated summary")
    category: str = Field(
        ..., description="Predicted content category (e.g. tech, finance)"
    )
    priority: str = Field(
        ..., description="Priority level: low / medium / high"
    )


class HealthComponent(BaseModel):
    status: str
    detail: str = ""


class HealthResponse(BaseModel):
    status: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    gemini: HealthComponent
    qdrant: HealthComponent


class ErrorResponse(BaseModel):
    detail: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
