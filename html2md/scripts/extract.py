"""Extract main content and media from HTML."""

from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup
import trafilatura
from trafilatura import metadata
from readability import Document

from models import ContentBlock, ExtractedContent, MediaItem


def extract_content(html: str, canonical_url: str) -> ExtractedContent:
    title = "Untitled"
    author = None
    publish_date = None
    extracted_text = None

    try:
        extracted_text = trafilatura.extract(html)
        meta = metadata.extract_metadata(html)
        if meta:
            if meta.title:
                title = meta.title
            author = meta.author
            publish_date = meta.date
    except Exception:
        extracted_text = None

    if not extracted_text:
        doc = Document(html)
        title = doc.short_title() or title
        extracted_text = BeautifulSoup(doc.summary(), "lxml").get_text("\n")

    soup = BeautifulSoup(html, "lxml")
    if title == "Untitled":
        page_title = soup.find("title")
        if page_title and page_title.get_text(strip=True):
            title = page_title.get_text(strip=True)

    text_blocks = [
        ContentBlock(text=block.strip())
        for block in extracted_text.split("\n")
        if block.strip()
    ]

    images: list[MediaItem] = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        images.append(MediaItem(type="image", url=urljoin(canonical_url, src)))

    videos: list[MediaItem] = []
    for video in soup.find_all("video"):
        src = video.get("src")
        if not src:
            source = video.find("source")
            src = source.get("src") if source else None
        if not src:
            continue
        videos.append(MediaItem(type="video", url=urljoin(canonical_url, src)))

    links = [
        urljoin(canonical_url, link["href"]) for link in soup.find_all("a", href=True)
    ]

    return ExtractedContent(
        title=title,
        author=author,
        publish_date=publish_date,
        canonical_url=canonical_url,
        text_blocks=text_blocks,
        images=images,
        videos=videos,
        links=links,
    )
