"""Document validation."""

from __future__ import annotations

import re

from config import KEYWORDS_MAX, KEYWORDS_MIN, SUMMARY_MAX_WORDS, SUMMARY_MIN_WORDS


def validate_document(markdown: str) -> None:
    sections = ["# ", "## Sources", "## Summary", "## Keywords", "## Content"]
    positions = []
    for section in sections:
        idx = markdown.find(section)
        if idx == -1:
            raise ValueError(f"Missing section: {section}")
        positions.append(idx)
    if positions != sorted(positions):
        raise ValueError("Sections are out of order")

    summary_text = _extract_section(markdown, "## Summary", "## Keywords")
    summary_words = re.findall(r"\b\w+\b", summary_text)
    if not (SUMMARY_MIN_WORDS <= len(summary_words) <= SUMMARY_MAX_WORDS):
        raise ValueError("Summary word count out of range")

    keywords_text = _extract_section(markdown, "## Keywords", "## Content")
    keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
    if not (KEYWORDS_MIN <= len(keywords) <= KEYWORDS_MAX):
        raise ValueError("Keywords count out of range")

    sources_text = _extract_section(markdown, "## Sources", "## Summary")
    if "Source URL" not in sources_text:
        raise ValueError("Sources missing URL")
    if "Publish Date" not in sources_text and "Generated Date" not in sources_text:
        raise ValueError("Sources missing date")


def _extract_section(markdown: str, start: str, end: str) -> str:
    start_idx = markdown.find(start)
    end_idx = markdown.find(end)
    if start_idx == -1 or end_idx == -1:
        return ""
    return markdown[start_idx + len(start) : end_idx].strip()
