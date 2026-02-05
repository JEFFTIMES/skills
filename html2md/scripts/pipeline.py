"""Pipeline orchestrator and CLI entrypoint."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from config import DEFAULT_LANGUAGE, MAX_IMAGES, MAX_VIDEOS, MEDIA_TIMEOUT_SECONDS
from extract import extract_content
from fetch import fetch_html
from media import capture_video_snapshots, download_images
from models import RenderInput, SkillResult
from render import render_markdown
from topic_filter import filter_by_topic
from translate import normalize_blocks
from utils import build_output_basename


def run_skill(
    url: str,
    output_dir: str,
    topic_focus: str | None = None,
    language: str = DEFAULT_LANGUAGE,
    max_images: int = MAX_IMAGES,
    max_videos: int = MAX_VIDEOS,
    skip_media: bool = False,
    use_headless: bool = False,
) -> SkillResult:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    assets_dir = output_path / "media"
    assets_dir.mkdir(parents=True, exist_ok=True)

    html, canonical_url = fetch_html(url, use_headless=use_headless)
    extracted = extract_content(html, canonical_url)

    blocks = extracted.text_blocks
    if topic_focus:
        blocks = filter_by_topic(blocks, topic_focus)
    blocks = normalize_blocks(blocks)

    block_texts = [block.text for block in blocks]
    content_text = "\n\n".join(block_texts)

    if skip_media:
        images = extracted.images
        videos = extracted.videos
    else:
        images = download_images(
            extracted.images,
            str(assets_dir),
            timeout=MEDIA_TIMEOUT_SECONDS,
            max_items=max_images,
        )
        videos = capture_video_snapshots(
            extracted.videos,
            str(assets_dir),
            max_items=max_videos,
        )

    sources = {
        "url": extracted.canonical_url,
        "publish_date": extracted.publish_date or "",
        "generated_date": datetime.now(timezone.utc).date().isoformat(),
    }

    content_markdown = _build_content_markdown(
        block_texts,
        images,
        videos,
        extracted.links,
    )

    render_input = RenderInput(
        title=extracted.title,
        summary="",
        keywords=[],
        sources=sources,
        content_markdown=content_markdown,
        images=images,
        videos=videos,
    )
    markdown = render_markdown(render_input)

    base_name = build_output_basename(
        title=extracted.title,
        source_url=extracted.canonical_url,
        publish_date=extracted.publish_date,
        generated_date=sources["generated_date"],
    )
    markdown_path = _unique_path(output_path, base_name, ".md")
    markdown_path.write_text(markdown, encoding="utf-8")

    metadata_path = _unique_path(output_path, base_name, ".json")
    metadata_path.write_text(
        json.dumps(extracted.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return SkillResult(
        markdown_path=str(markdown_path),
        assets_dir=str(assets_dir),
        metadata_path=str(metadata_path),
    )


def _build_content_markdown(
    blocks: list[str],
    images: list,
    videos: list,
    links: list[str],
) -> str:
    paragraphs = [block.strip() for block in blocks if block.strip()]
    media_lines: list[str] = []

    image_links = _unique_media_links(images, "local_path")
    for link in image_links:
        media_lines.append(f"![image]({link})")

    video_snapshots = _unique_media_links(videos, "snapshot_path")
    for idx, snapshot in enumerate(video_snapshots, start=1):
        media_lines.append(f"![video snapshot {idx}]({snapshot})")

    insertion_map = _build_media_insertion_map(len(paragraphs), media_lines)

    content_sections: list[str] = []
    media_heading_added = False
    for idx, paragraph in enumerate(paragraphs):
        content_sections.append(paragraph)
        if idx in insertion_map:
            if not media_heading_added:
                content_sections.append("### Media")
                media_heading_added = True
            content_sections.extend(insertion_map[idx])

    if not paragraphs and media_lines:
        content_sections.append("### Media")
        content_sections.extend(media_lines)

    link_lines = _unique_links(links)
    if link_lines:
        content_sections.append("### Links")
        content_sections.extend(f"- {link}" for link in link_lines)

    return "\n\n".join(section for section in content_sections if section.strip())


def _build_media_insertion_map(
    paragraph_count: int,
    media_lines: list[str],
) -> dict[int, list[str]]:
    if not media_lines:
        return {}
    if paragraph_count == 0:
        return {}

    insertion_map: dict[int, list[str]] = {}
    for index, media in enumerate(media_lines, start=1):
        position = int(index * paragraph_count / (len(media_lines) + 1))
        insertion_map.setdefault(position, []).append(media)
    return insertion_map


def _unique_media_links(items: list, attr: str) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        link = getattr(item, attr, None) or getattr(item, "url", None)
        if link and link.startswith("data:"):
            continue
        if link and "adsct" in link:
            continue
        if not link or link in seen:
            continue
        seen.add(link)
        output.append(link)
    return output


def _unique_links(links: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for link in links:
        parsed = urlparse(link)
        if parsed.scheme not in {"http", "https"}:
            continue
        if link in seen:
            continue
        seen.add(link)
        output.append(link)
    return output


def _unique_path(output_dir: Path, base_name: str, suffix: str) -> Path:
    candidate = output_dir / f"{base_name}{suffix}"
    counter = 2
    while candidate.exists():
        candidate = output_dir / f"{base_name}-{counter}{suffix}"
        counter += 1
    return candidate


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert a webpage to markdown.")
    parser.add_argument("--url", required=True, help="Webpage URL")
    parser.add_argument("--out", required=True, help="Output directory")
    parser.add_argument("--topic", default=None, help="Topic focus")
    parser.add_argument("--lang", default=DEFAULT_LANGUAGE, help="Target language")
    parser.add_argument(
        "--max-images",
        type=int,
        default=MAX_IMAGES,
        help="Max number of images to download (0 for no limit)",
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=MAX_VIDEOS,
        help="Max number of videos to snapshot (0 for no limit)",
    )
    parser.add_argument(
        "--no-media",
        action="store_true",
        help="Skip downloading media; use remote URLs instead",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Use headless browser fallback on 401/403 responses",
    )
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()
    run_skill(
        url=args.url,
        output_dir=args.out,
        topic_focus=args.topic,
        language=args.lang,
        max_images=args.max_images,
        max_videos=args.max_videos,
        skip_media=args.no_media,
        use_headless=args.headless,
    )


if __name__ == "__main__":
    main()
