"""Pydantic models for the skill pipeline."""

from typing import Literal

from pydantic import BaseModel


class ContentBlock(BaseModel):
    text: str
    language: str | None = None
    score: float | None = None


class MediaItem(BaseModel):
    type: Literal["image", "video"]
    url: str
    local_path: str | None = None
    snapshot_path: str | None = None


class ExtractedContent(BaseModel):
    title: str
    author: str | None = None
    publish_date: str | None = None
    canonical_url: str
    text_blocks: list[ContentBlock]
    images: list[MediaItem]
    videos: list[MediaItem]
    links: list[str]


class SummaryResult(BaseModel):
    summary: str
    keywords: list[str]


class RenderInput(BaseModel):
    title: str
    summary: str
    keywords: list[str]
    sources: dict[str, str]
    content_markdown: str
    images: list[MediaItem]
    videos: list[MediaItem]


class SkillResult(BaseModel):
    markdown_path: str
    assets_dir: str
    metadata_path: str | None = None
