#!/usr/bin/env python3
"""Extract Chinese text blocks from a Markdown file into placeholders.

Creates a sibling .en.md file with placeholders and writes a blocks file.

Usage:
  python scripts/extract_cn_blocks.py --input path/to/foo.md

Outputs:
  - Sibling file: foo.en.md (or foo.zh.md -> foo.en.md)
  - Blocks file: foo.en.blocks.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from shutil import copyfile
from typing import Tuple

CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract Chinese blocks from Markdown")
    parser.add_argument("--input", required=True, help="Path to Chinese Markdown file")
    parser.add_argument("--blocks", help="Optional path to blocks json output")
    parser.add_argument("--output", help="Optional path to skeleton .en.md output")
    return parser.parse_args()


def compute_output_path(input_path: Path) -> Path:
    name = input_path.name
    if name.endswith(".zh.md"):
        return input_path.with_name(name[:-6] + ".en.md")
    if name.endswith(".md") and not name.endswith(".en.md"):
        return input_path.with_name(name[:-3] + ".en.md")
    return input_path.with_name(name + ".en.md")


def split_prefix(line: str) -> Tuple[str, str]:
    # Preserve common markdown prefixes so structure remains intact.
    patterns = [
        r"^(\s*#{1,6}\s+)(.*)$",  # headings
        r"^(\s*[-*+]\s+\[[ xX]\]\s+)(.*)$",  # task list
        r"^(\s*(?:[-*+]|\d+\.)\s+)(.*)$",  # list items
        r"^(\s*(?:>\s+)+)(.*)$",  # blockquote
    ]
    for pat in patterns:
        m = re.match(pat, line)
        if m:
            return m.group(1), m.group(2)
    return "", line


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    output_path = Path(args.output).resolve() if args.output else compute_output_path(input_path)
    blocks_path = Path(args.blocks).resolve() if args.blocks else output_path.with_suffix(".blocks.json")

    copyfile(input_path, output_path)

    lines = output_path.read_text(encoding="utf-8").splitlines()

    blocks = []
    out_lines = []
    in_front_matter = False
    in_fenced_code = False

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()

        if idx == 1 and stripped == "---":
            in_front_matter = True
            out_lines.append(line)
            continue
        if in_front_matter:
            out_lines.append(line)
            if stripped == "---":
                in_front_matter = False
            continue

        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fenced_code = not in_fenced_code
            out_lines.append(line)
            continue
        if in_fenced_code:
            out_lines.append(line)
            continue

        prefix, remainder = split_prefix(line)
        if CJK_RE.search(remainder or ""):
            block_index = len(blocks) + 1
            placeholder = f"[[CN2EN_BLOCK_{block_index:04d}]]"
            blocks.append({
                "index": block_index,
                "placeholder": placeholder,
                "text": remainder,
            })
            out_lines.append(prefix + placeholder)
        else:
            out_lines.append(line)

    output_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    blocks_path.write_text(json.dumps(blocks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"output": str(output_path), "blocks": str(blocks_path), "count": len(blocks)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
