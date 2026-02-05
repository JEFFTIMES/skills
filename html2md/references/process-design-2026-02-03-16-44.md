# html2md process design (2026-02-03 16:44)

1. Read `tests/urls.md` and parse the list of URLs.
2. For each URL, run the pipeline entrypoint in `scripts/pipeline.py`.
3. Fetch HTML:
   - Try direct HTTP GET.
   - If 401/403, fall back to the Jina proxy.
   - If a local HTML export is provided (option-2), use that file instead of fetching.
4. Extract main content and metadata (`scripts/skill/extract.py`): title, publish date, text blocks, images, videos, links.
5. Optionally filter blocks by topic (`scripts/skill/topic_filter.py`).
6. Detect language and normalize text to English (`scripts/skill/translate.py`).
7. Download images and capture video snapshots (`scripts/skill/media.py`) into `tmp/assets/`.
8. Summarize to 200-300 words and extract 8-15 keywords (`scripts/skill/summarize.py`).
9. Render markdown via `assets/templates/document.md.j2` (`scripts/skill/render.py`).
10. Validate required structure and counts (`scripts/skill/validate.py`).
11. Build output filename using the naming policy (date + domain + title).
12. Write `.md` and `.json` metadata to `tmp/` (and any intermediate files to `tmp/` or `tmp/cache/`).
