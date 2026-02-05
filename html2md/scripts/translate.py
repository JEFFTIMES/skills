"""Language detection and translation utilities."""

from __future__ import annotations

from langdetect import detect

from models import ContentBlock


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "unknown"


def translate_to_en(text: str, source_lang: str) -> str:
    if source_lang in {"en", "unknown"}:
        return text
    return text


def normalize_blocks(blocks: list[ContentBlock]) -> list[ContentBlock]:
    normalized: list[ContentBlock] = []
    for block in blocks:
        language = detect_language(block.text)
        text = translate_to_en(block.text, language)
        normalized.append(ContentBlock(text=text, language=language, score=block.score))
    return normalized
