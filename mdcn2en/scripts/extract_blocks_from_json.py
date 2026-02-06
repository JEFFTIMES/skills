#!/usr/bin/env python3
"""Extract block texts from a blocks JSON file.

Usage:
  python scripts/extract_blocks_from_json.py --input path/to/foo.en.blocks.json

Outputs:
  - Prints lines like "0001\t<text>" to stdout by default.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract block texts from blocks JSON")
    parser.add_argument("--input", required=True, help="Path to blocks JSON file")
    parser.add_argument("--output", help="Optional output text file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    blocks = json.loads(input_path.read_text(encoding="utf-8"))
    lines = []
    for b in blocks:
        index = int(b.get("index", 0))
        text = b.get("text", "")
        lines.append(f"{index:04d}\t{text}")

    output = "\n".join(lines) + ("\n" if lines else "")
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
