from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY", "")
    )
    gemini_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    )
    qdrant_url: str = field(
        default_factory=lambda: os.getenv("QDRANT_URL", "http://localhost:6333")
    )
    qdrant_api_key: str = field(
        default_factory=lambda: os.getenv("QDRANT_API_KEY", "")
    )
    qdrant_collection: str = field(
        default_factory=lambda: os.getenv("QDRANT_COLLECTION", "omnirarg_docs")
    )
    vector_dimension: int = 768
    app_host: str = field(
        default_factory=lambda: os.getenv("APP_HOST", "0.0.0.0")
    )
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "info")
    )

    def validate(self) -> None:
        missing: list[str] = []
        if not self.gemini_api_key:
            missing.append("GEMINI_API_KEY")
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}"
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()
