"""Shared helpers."""

from __future__ import annotations

import re
import unicodedata
from urllib.parse import urlparse


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "document"


def build_output_basename(
    title: str,
    source_url: str,
    publish_date: str | None,
    generated_date: str,
) -> str:
    domain = urlparse(source_url).hostname or "source"
    domain = domain.replace("www.", "")
    date_part = (publish_date or generated_date).replace("-", "")
    title_part = slugify(title)
    return f"{date_part}-{domain}-{title_part}"
