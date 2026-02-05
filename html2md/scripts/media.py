"""Download images and capture video snapshots."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import requests

from models import MediaItem


def download_images(
    items: list[MediaItem],
    assets_dir: str,
    timeout: int = 12,
    max_items: int | None = None,
) -> list[MediaItem]:
    Path(assets_dir).mkdir(parents=True, exist_ok=True)
    output_items: list[MediaItem] = []
    for item in _limit_items(items, max_items):
        if item.type != "image":
            output_items.append(item)
            continue
        try:
            response = requests.get(item.url, timeout=timeout)
            response.raise_for_status()
            ext = _guess_extension(item.url) or "jpg"
            digest = hashlib.sha256(item.url.encode("utf-8")).hexdigest()[:12]
            filename = f"image-{digest}.{ext}"
            file_path = Path(assets_dir) / filename
            file_path.write_bytes(response.content)
            local_path = os.path.join(Path(assets_dir).name, filename)
            output_items.append(item.model_copy(update={"local_path": local_path}))
        except Exception:
            output_items.append(item)
    return output_items


def capture_video_snapshots(
    items: list[MediaItem],
    assets_dir: str,
    max_items: int | None = None,
) -> list[MediaItem]:
    Path(assets_dir).mkdir(parents=True, exist_ok=True)
    output_items: list[MediaItem] = []
    for item in _limit_items(items, max_items):
        if item.type != "video":
            output_items.append(item)
            continue
        snapshot_path = _snapshot_video(item.url, assets_dir)
        if snapshot_path:
            local_path = os.path.join(Path(assets_dir).name, snapshot_path)
            output_items.append(item.model_copy(update={"snapshot_path": local_path}))
        else:
            output_items.append(item)
    return output_items


def _guess_extension(url: str) -> str | None:
    path = urlparse(url).path
    if "." not in path:
        return None
    ext = path.rsplit(".", 1)[-1].lower()
    if len(ext) > 5:
        return None
    return ext


def _limit_items(items: list[MediaItem], max_items: int | None) -> list[MediaItem]:
    if max_items is None or max_items <= 0:
        return list(items)
    return list(items)[:max_items]


def _snapshot_video(url: str, assets_dir: str) -> str | None:
    if not shutil.which("ffmpeg"):
        return None
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    filename = f"video-{digest}.jpg"
    file_path = Path(assets_dir) / filename
    command = [
        "ffmpeg",
        "-y",
        "-i",
        url,
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(file_path),
    ]
    try:
        subprocess.run(
            command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return filename
    except Exception:
        return None
