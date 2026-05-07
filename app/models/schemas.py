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


class DocumentResponse(BaseModel):
    document_id: str
    source: str
    summary: str
    category: str
    priority: str
    chunk_count: int = 0


class DocumentListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[DocumentResponse]


class QueryRequest(BaseModel):
    question: str = Field(
        ..., min_length=1, description="Natural-language query"
    )
    top_k: int = Field(
        default=5, ge=1, le=100, description="Number of results to return"
    )


class QueryResult(BaseModel):
    chunk_content: str
    score: float
    metadata: dict[str, Any]


class QueryResponse(BaseModel):
    results: list[QueryResult]


class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    category_distribution: dict[str, int]
    priority_distribution: dict[str, int]


class MetadataUpdateRequest(BaseModel):
    summary: str | None = None
    category: str | None = None
    priority: str | None = None


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
