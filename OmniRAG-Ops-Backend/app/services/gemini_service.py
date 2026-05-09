from __future__ import annotations

import logging

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.core.config import get_settings
from app.models.schemas import MetadataEnrichment

logger = logging.getLogger(__name__)

_SUMMARY_TEMPLATE = """You are a metadata extraction assistant.
Analyze the following document content and produce a JSON object with exactly three keys:

- "summary": a concise 2-3 sentence summary of the content
- "category": a single-word or short-phrase category (e.g. technology, finance, healthcare, education)
- "priority": one of "low", "medium", or "high" based on how time-sensitive or critical the content appears

Respond ONLY with valid JSON. Do not include markdown fences.

Content:
{content}

{format_instructions}
"""


def _build_llm() -> ChatGoogleGenerativeAI:
    settings = get_settings()
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.1,
    )


async def enrich_metadata(content: str) -> MetadataEnrichment:
    parser = PydanticOutputParser(pydantic_object=MetadataEnrichment)
    prompt = PromptTemplate(
        template=_SUMMARY_TEMPLATE,
        input_variables=["content"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        },
    )
    llm = _build_llm()
    chain = prompt | llm | parser
    try:
        result: MetadataEnrichment = await chain.ainvoke({"content": content})
        return result
    except Exception:
        logger.exception("Gemini metadata enrichment failed")
        return MetadataEnrichment(
            summary="Failed to generate summary.",
            category="unknown",
            priority="low",
        )


async def check_connectivity() -> tuple[bool, str]:
    try:
        llm = _build_llm()
        response = await llm.ainvoke("Respond with just the word: ok")
        is_ok = response.content.strip().lower() == "ok"
        return is_ok, "reachable" if is_ok else "unexpected response"
    except Exception as exc:
        return False, str(exc)
