#!/usr/bin/env python3
"""Append glossary entries to references/glossary.jsonl.

Usage (batch dict):
  python scripts/append_glossary.py --input path/to/glossary.json --source "path.md" --context "short snippet"

Input formats supported:
- JSON dict: {"术语": "Term", "科研": "research"}
- JSON list: [{"zh": "术语", "en": "Term", "source": "...", "context": "..."}, ...]
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append glossary terms to glossary.jsonl")
    parser.add_argument("--input", required=True, help="Path to glossary JSON file")
    parser.add_argument("--source", help="Default source for dict input")
    parser.add_argument("--context", help="Default context for dict input")
    return parser.parse_args()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_entries(data, default_source: str | None, default_context: str | None) -> List[dict]:
    entries: List[dict] = []
    if isinstance(data, dict):
        if not default_source or not default_context:
            raise SystemExit("--source and --context are required when input is a JSON dict")
        for zh, en in data.items():
            entries.append({
                "zh": str(zh),
                "en": str(en),
                "source": default_source,
                "context": default_context,
                "added_at": now_iso(),
            })
        return entries

    if isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                raise SystemExit("List entries must be JSON objects")
            if "zh" not in item or "en" not in item:
                raise SystemExit("Each entry must include 'zh' and 'en'")
            source = item.get("source") or default_source
            context = item.get("context") or default_context
            if not source or not context:
                raise SystemExit("Each entry requires 'source' and 'context'")
            entries.append({
                "zh": str(item["zh"]),
                "en": str(item["en"]),
                "source": str(source),
                "context": str(context),
                "added_at": item.get("added_at") or now_iso(),
            })
        return entries

    raise SystemExit("Unsupported input JSON format")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    data = json.loads(input_path.read_text(encoding="utf-8"))
    entries = normalize_entries(data, args.source, args.context)

    glossary_path = Path(__file__).resolve().parents[1] / "references" / "glossary.jsonl"
    glossary_path.parent.mkdir(parents=True, exist_ok=True)

    with glossary_path.open("a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
