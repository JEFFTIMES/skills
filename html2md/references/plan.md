## html2md plan

1. Fetch HTML (URL or local file).
2. Extract title, publish date, text blocks, images, videos, links.
3. Optionally filter text blocks by topic.
4. Normalize text blocks to English.
5. Download images and capture video snapshots to `output/media/`.
6. Render markdown via `assets/templates/document.md.j2`.
7. Render markdown with empty Summary/Keywords.
8. Read the output markdown, then provide a 1-100 word summary and 5-10 keywords.
9. Update the markdown via `update_summary_and_keywords.py`.
10. Append Media and Links subsections within Content when available (http/https only), inserting media near related paragraphs when possible.
11. Validate ordering: Title, Sources, Summary, Keywords, Content.
12. Save markdown and metadata JSON to `output/`.
13. For large pages, cap image/video downloads to keep the pipeline responsive.
14. If media downloads stall, rerun with `--no-media` to keep remote URLs.
15. If 401/403 blocks occur, fall back to Jina; use `--headless` only when necessary.
16. Headless mode uses a reduced per-selector wait to avoid long stalls.
17. Skip data URI media links.
18. Skip known ad tracker media links (e.g., adsct).
