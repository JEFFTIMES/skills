---
name: mdcn2en
description: Translate Chinese Markdown (.md) files into English while preserving Markdown structure. Use only for Markdown files and when asked to translate Chinese Markdown to English, create a sibling .en.md file, keep YAML front matter untouched, and maintain a term glossary/translation memory.
---

# mdcn2en

## Workflow

1) Confirm input .md file path and desired output name (default: `foo.md` -> `foo.en.md`).
2) Run `scripts/extract_cn_blocks.py` to create the skeleton `.en.md` and the blocks file.
   - The skeleton keeps YAML front matter, code blocks, and Markdown structure.
   - Chinese text is replaced by indexed placeholders.
3) Run `scripts/extract_blocks_from_json.py` to list the blocks for translation.
4) Translate the extracted blocks one by one, applying glossary terms where appropriate.
5) Run `scripts/insert_en_blocks.py` to replace placeholders in the skeleton with translations.
6) Append stable new terms to `references/glossary.jsonl` using `scripts/append_glossary.py` in batch.

## Script Usage

### Extract blocks

```bash
python mdcn2en/scripts/extract_cn_blocks.py --input path/to/foo.md
```

This creates:

- `path/to/foo.en.md` with placeholders
- `path/to/foo.en.blocks.json` with extracted blocks

### List blocks for translation

```bash
python mdcn2en/scripts/extract_blocks_from_json.py --input path/to/foo.en.blocks.json
```

### Insert translations

```bash
python mdcn2en/scripts/insert_en_blocks.py --input path/to/foo.en.md --translations path/to/translated.json
```

Translations file formats:

- JSON list: `[{"index": 1, "text": "..."}]`
- JSON dict: `{ "[[CN2EN_BLOCK_0001]]": "..." }`
- JSONL: one object per line with `index` or `placeholder` and `text`

### Append glossary (batch)

```bash
python mdcn2en/scripts/append_glossary.py --input path/to/glossary.json --source "path.md" --context "short snippet"
```

Input formats:

- JSON dict: `{ "术语": "Term", "科研": "research" }` (requires `--source` and `--context`)
- JSON list: `[{"zh": "术语", "en": "Term", "source": "...", "context": "..."}, ...]`

## Resources

- `references/output-conventions.md`: naming rules and file placement.
- `references/ignore-rules.md`: what to preserve and never translate.
- `references/glossary.jsonl`: append-only term base.
- `references/terms.md`: guidance for adding stable glossary entries.
- `scripts/append_glossary.py`: helper to append stable terms to the glossary.
- `scripts/extract_cn_blocks.py`: create a skeleton .en.md file and extract placeholders into a blocks file.
- `scripts/extract_blocks_from_json.py`: list block texts from a blocks JSON file.
- `scripts/insert_en_blocks.py`: insert translated blocks into the skeleton .en.md file.

## Term Base Format

Each line in `references/glossary.jsonl` is a JSON object:

- `zh`: Chinese term
- `en`: English term
- `source`: where the term came from (file path or context)
- `context`: short snippet to clarify meaning
- `added_at`: ISO 8601 timestamp

Append only when the translation is stable and unambiguous.
