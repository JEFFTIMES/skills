"""Update markdown with LLM-provided summary and keywords JSON blocks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

def update_markdown(markdown: str, summary: str, keywords: list[str]) -> str:
    lines = markdown.splitlines()
    summary_block = ["## Summary", summary.strip()]
    keywords_block = ["## Keywords", ", ".join(keywords)]

    def replace_section(title: str, new_block: list[str]) -> None:
        try:
            start = lines.index(title)
        except ValueError:
            lines.extend(["", *new_block])
            return

        end = len(lines)
        for idx in range(start + 1, len(lines)):
            if lines[idx].startswith("## "):
                end = idx
                break
        lines[start:end] = new_block + [""]

    replace_section("## Summary", summary_block)
    replace_section("## Keywords", keywords_block)
    return "\n".join(lines).strip() + "\n"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update markdown summary/keywords from JSON blocks."
    )
    parser.add_argument("--markdown", required=True, help="Path to markdown file")
    parser.add_argument(
        "--summary-json",
        required=True,
        help='JSON object like {"summary": "..."}',
    )
    parser.add_argument(
        "--keywords-json",
        required=True,
        help='JSON object like {"keywords": ["k1", "k2"]}',
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    summary_payload = json.loads(args.summary_json)
    keywords_payload = json.loads(args.keywords_json)

    summary = summary_payload.get("summary", "").strip()
    keywords = keywords_payload.get("keywords", [])
    if not isinstance(keywords, list):
        raise ValueError("keywords must be a list")

    markdown_path = Path(args.markdown)
    markdown = markdown_path.read_text(encoding="utf-8")
    updated = update_markdown(markdown, summary, keywords)
    markdown_path.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
