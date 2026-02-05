"""Fetch HTML from a URL."""

from __future__ import annotations

import requests
from bs4 import BeautifulSoup


def fetch_html(url: str, timeout: int = 20, use_headless: bool = False) -> tuple[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(url, timeout=timeout, headers=headers)
    if response.status_code in {401, 403}:
        if use_headless:
            try:
                html, canonical_url = headless_fetch(url, timeout=timeout)
                return html, canonical_url
            except Exception:
                pass
        proxy_url = _jina_proxy(url)
        response = requests.get(proxy_url, timeout=timeout, headers=headers)
    response.raise_for_status()
    html = response.text
    canonical_url = url
    soup = BeautifulSoup(html, "lxml")
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        canonical_url = canonical["href"].strip()
    return html, canonical_url


def _jina_proxy(url: str) -> str:
    if url.startswith("https://"):
        return f"https://r.jina.ai/https://{url[len('https://') :]}"
    if url.startswith("http://"):
        return f"https://r.jina.ai/http://{url[len('http://') :]}"
    return f"https://r.jina.ai/http://{url}"


def headless_fetch(url: str, timeout: int = 30) -> tuple[str, str]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is not installed.") from exc

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
        _accept_consent(page)
        _accept_iframe_consent(page)
        _wait_for_article(page, timeout)
        html = page.content()
        browser.close()

    canonical_url = url
    soup = BeautifulSoup(html, "lxml")
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        canonical_url = canonical["href"].strip()
    return html, canonical_url


def _accept_consent(page) -> None:
    consent_texts = ["Accept", "I agree", "Agree", "Accept all"]
    for text in consent_texts:
        try:
            button = page.get_by_role("button", name=text)
            if button.is_visible():
                button.click()
                page.wait_for_timeout(1000)
                return
        except Exception:
            continue


def _accept_iframe_consent(page) -> None:
    consent_texts = ["Accept", "I agree", "Agree", "Accept all"]
    try:
        for frame in page.frames:
            for text in consent_texts:
                try:
                    button = frame.get_by_role("button", name=text)
                    if button.is_visible():
                        button.click()
                        page.wait_for_timeout(1000)
                        return
                except Exception:
                    continue
    except Exception:
        return


def _wait_for_article(page, timeout: int) -> None:
    selectors = [
        "article",
        "[data-testid='ArticleBody']",
        "[data-testid='Body']",
        "[data-testid='BodyText']",
        "[data-testid='Paragraph']",
        "[data-testid='StoryBody']",
        "[class*='article-body']",
    ]
    per_selector_timeout = max(1000, int(timeout * 1000 / max(len(selectors), 1)))
    for selector in selectors:
        try:
            page.wait_for_selector(selector, timeout=per_selector_timeout)
            return
        except Exception:
            continue
