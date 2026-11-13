"""Download live pages from trusted sources (data/trusted_sources.json) into
data/sources/fetched/ as Markdown, then rebuild the index.

Run this on the Spark (it has internet access). Your residents' queries never leave
the machine - only these public pages are downloaded.

    python scripts/fetch_sources.py
    python scripts/fetch_sources.py --url https://www.gov.uk/some-page --category housing
"""
import argparse
import asyncio
import json
import re
from datetime import date

import httpx
from bs4 import BeautifulSoup

import _path  # noqa: F401
from backend.config import settings
from backend.rag.store import store

OUT = settings.sources_dir / "fetched"


def slug(url: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", url.lower().split("//", 1)[-1]).strip("-")[:90]


def html_to_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.find("h1") or soup.title or soup).get_text(" ", strip=True)[:150]
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "noscript"]):
        tag.decompose()
    main = soup.find("main") or soup.find(id="content") or soup.body or soup
    lines = []
    for el in main.find_all(["h1", "h2", "h3", "p", "li", "td"]):
        t = el.get_text(" ", strip=True)
        if len(t) > 2:
            lines.append(("## " + t) if el.name in ("h2", "h3") else t)
    return title, "\n\n".join(dict.fromkeys(lines))


async def fetch_one(client, item):
    url = item["url"]
    try:
        r = await client.get(url)
        r.raise_for_status()
    except Exception as e:  # noqa: BLE001
        print(f"  SKIP {url}: {e}")
        return False
    title, text = html_to_text(r.text)
    if len(text) < 200:
        print(f"  SKIP {url}: too little text")
        return False
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{slug(url)}.md").write_text(
        f"---\ntitle: {title}\nurl: {url}\nprovider: {item.get('provider', '')}\n"
        f"category: {item.get('category', 'general')}\nlast_checked: {date.today()}\n---\n{text}\n",
        encoding="utf-8",
    )
    print(f"  OK   {url}  ({len(text)} chars)")
    return True


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url")
    ap.add_argument("--category", default="general")
    ap.add_argument("--provider", default="")
    args = ap.parse_args()
    items = [{"url": args.url, "category": args.category, "provider": args.provider}] if args.url else \
        json.loads(settings.trusted_sources_file.read_text())["fetch_urls"]
    headers = {"User-Agent": "PeoplesGuide/1.0 (hackathon prototype; public-services research)"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30) as client:
        ok = 0
        for item in items:
            ok += await fetch_one(client, item)
            await asyncio.sleep(0.5)  # be polite
    print(f"Fetched {ok}/{len(items)} pages. Rebuilding index ...")
    print(await store.build())


if __name__ == "__main__":
    asyncio.run(main())
