"""Markdown rendering."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from models import RenderInput


def render_markdown(data: RenderInput) -> str:
    template_path = Path(__file__).resolve().parents[1] / "assets" / "templates"
    env = Environment(loader=FileSystemLoader(str(template_path)))
    template = env.get_template("document.md.j2")
    return template.render(**data.model_dump())
