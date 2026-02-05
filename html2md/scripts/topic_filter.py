"""Filter content blocks by topic relevance."""

from __future__ import annotations

import re

from models import ContentBlock


def filter_by_topic(blocks: list[ContentBlock], topic: str) -> list[ContentBlock]:
    if not topic:
        return blocks
    keywords = [word for word in re.split(r"\W+", topic.lower()) if word]
    if not keywords:
        return blocks

    filtered = [
        block
        for block in blocks
        if any(word in block.text.lower() for word in keywords)
    ]
    return filtered if filtered else blocks
