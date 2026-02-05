---
name: html2md
description: Use this skill to convert a webpage (URL or local HTML) into a structured markdown document. Keep the title, topic-related text, images, videos, links; filter out ads and unrelated components. Add a Sources block (title, source URL, date) at the top, then Summary (<100 words), then Keywords (5-10 entries), then Content.
---

# HTML to Markdown converting guide

## Quick start

```bash
PYTHONPATH=scripts python -m pipeline --url <url> --out output --no-media [--topic "<topic>"]
```

## Workflow 

1. Run `pipeline.py` to generate the draft markdown with empty Summary/Keywords.
2. You review the content and compose summary + keywords.
3. Update the markdown with `update_summary_and_keywords.py`.
4. Validate document structure and save outputs.


## Required output format

- Sections must appear in order: Title, Sources, Summary, Keywords, Content.
- Keep contents (text, images, video snapshots, links) as close to the original placement as possible.
- Summary must be 1-100 words.
- Keywords must contain 5-10 entries.
- Sources must include source URL and publish date (or generated date).
- Media references must be relative local paths if downloaded.
- Content should include a Media subsection for images/video snapshots and a Links subsection when available, inserted near related paragraphs when possible.
- Links should include only http/https URLs.
- Exclude data URIs from media references.
- Exclude ad tracker media URLs (e.g., adsct).

## Tools scripts

- Use the module stubs in `scripts/`:
  - `fetch.py` for HTML retrieval (optional headless fallback). CLI: none.
  - `extract.py` for readability/trafilatura extraction and media detection. CLI: none.
  - `topic_filter.py` for relevance filtering. CLI: none.
  - `media.py` for image download and video snapshots. CLI: none.
  - `update_summary_and_keywords.py` for JSON-based summary/keywords updates.
    - Options: `--markdown <path> --summary-json '{"summary":"..."}' --keywords-json '{"keywords":["k1","k2"]}'`
  - `render.py` for markdown rendering. CLI: none.
  - `validate.py` for output checks. CLI: none (import and call `validate_document`).
  - `utils.py` for helpers like slugify. CLI: none.
  - `pipeline.py` to orchestrate and save outputs.
    - Options: `--url <url> --out <dir> [--topic "<topic>"] [--lang <lang>] [--max-images N] [--max-videos N] [--no-media] [--headless]`
  

## References

- For detailed requirements, data models, and validation gates, read `references/plan.md`.
