import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "data" / "sources" / "official_pages.json"

SOURCES = [
    "https://www.gov.uk/universal-credit",
    "https://www.gov.uk/universal-credit/eligibility",
    "https://www.gov.uk/housing-and-universal-credit",
    "https://www.gov.uk/apply-council-tax-reduction",
    "https://www.gov.uk/if-youre-homeless-at-risk-of-homelessness",
]


def main():
    pages = []

    with httpx.Client(
        timeout=30,
        follow_redirects=True,
        headers={"User-Agent": "PeoplesGuideHackathonPrototype/0.1"},
    ) as client:
        for url in SOURCES:
            try:
                response = client.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                content = soup.find("main")

                if content is None:
                    raise ValueError("No main content found")

                for element in content.select("script, style, nav, form"):
                    element.decompose()

                text = content.get_text(separator="\n", strip=True)

                if len(text) < 100:
                    raise ValueError("Too little page content")

                title = (
                    soup.title.get_text(strip=True)
                    if soup.title
                    else str(response.url)
                )

                pages.append({
                    "source_id": f"source-{len(pages) + 1:03d}",
                    "title": title,
                    "url": str(response.url),
                    "retrieved_at": datetime.now(timezone.utc).isoformat(),
                    "text": text,
                })

                print(f"Saved: {title}")

            except (httpx.HTTPError, ValueError) as error:
                print(f"FAILED: {url} — {error}")

    if not pages:
        raise SystemExit("No pages downloaded. Existing data was preserved.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(pages, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nSaved {len(pages)} pages to {OUTPUT}")


if __name__ == "__main__":
    main()