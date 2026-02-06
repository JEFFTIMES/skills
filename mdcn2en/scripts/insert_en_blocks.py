#!/usr/bin/env python3
"""Insert translated English blocks into a skeleton Markdown file.

Usage:
  python scripts/insert_en_blocks.py --input path/to/foo.en.md --translations path/to/blocks.json

Translations file formats supported:
- JSON list: [{"index": 1, "text": "..."}, {"placeholder": "[[...]]", "text": "..."}]
- JSON dict: {"[[CN2EN_BLOCK_0001]]": "..."}
- JSONL: one JSON object per line with the same fields as list entries
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Insert translated blocks into Markdown skeleton")
    parser.add_argument("--input", required=True, help="Path to skeleton .en.md file")
    parser.add_argument("--translations", required=True, help="Path to translations json/jsonl")
    parser.add_argument("--output", help="Optional output path (default: overwrite input)")
    return parser.parse_args()


def load_translations(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding="utf-8")
    translations: Dict[str, str] = {}

    if path.suffix == ".jsonl":
        for line in text.splitlines():
            if not line.strip():
                continue
            obj = json.loads(line)
            if "placeholder" in obj:
                translations[obj["placeholder"]] = obj["text"]
            elif "index" in obj:
                placeholder = f"[[CN2EN_BLOCK_{int(obj['index']):04d}]]"
                translations[placeholder] = obj["text"]
            elif "text" in obj and "id" in obj:
                placeholder = f"[[CN2EN_BLOCK_{int(obj['id']):04d}]]"
                translations[placeholder] = obj["text"]
        return translations

    obj = json.loads(text)
    if isinstance(obj, dict):
        for k, v in obj.items():
            translations[str(k)] = str(v)
        return translations
    if isinstance(obj, list):
        for item in obj:
            if "placeholder" in item:
                translations[item["placeholder"]] = item["text"]
            elif "index" in item:
                placeholder = f"[[CN2EN_BLOCK_{int(item['index']):04d}]]"
                translations[placeholder] = item["text"]
        return translations

    raise SystemExit("Unsupported translations file format")


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    translations_path = Path(args.translations).resolve()
    if not translations_path.exists():
        raise SystemExit(f"Translations not found: {translations_path}")

    translations = load_translations(translations_path)
    content = input_path.read_text(encoding="utf-8")

    missing = [p for p in translations.keys() if p not in content]
    if missing:
        raise SystemExit("Some placeholders not found in input: " + ", ".join(missing[:5]))

    for placeholder, text in translations.items():
        content = content.replace(placeholder, text)

    output_path = Path(args.output).resolve() if args.output else input_path
    output_path.write_text(content, encoding="utf-8")

    print(json.dumps({"output": str(output_path), "count": len(translations)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
