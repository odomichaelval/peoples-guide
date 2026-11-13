"""Load source documents (Markdown with a small front-matter header) and chunk them."""
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Chunk:
    id: str
    text: str
    title: str
    url: str
    provider: str
    category: str
    meta: dict = field(default_factory=dict)


def parse_front_matter(raw: str) -> tuple[dict, str]:
    meta: dict = {}
    if raw.startswith("---"):
        end = raw.find("\n---", 3)
        if end != -1:
            for line in raw[3:end].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
            raw = raw[end + 4 :]
    return meta, raw.strip()


def chunk_text(text: str, max_chars: int = 1200, overlap: int = 150) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 2 <= max_chars:
            cur = f"{cur}\n\n{p}" if cur else p
        else:
            if cur:
                chunks.append(cur)
            while len(p) > max_chars:
                chunks.append(p[:max_chars])
                p = p[max_chars - overlap :]
            cur = (chunks[-1][-overlap:] + "\n\n" + p) if chunks else p
    if cur:
        chunks.append(cur)
    return chunks


def load_chunks(sources_dir: Path) -> list[Chunk]:
    out: list[Chunk] = []
    for path in sorted(sources_dir.rglob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        title = meta.get("title", path.stem.replace("-", " ").title())
        for i, piece in enumerate(chunk_text(body)):
            out.append(
                Chunk(
                    id=f"{path.stem}#{i}",
                    text=f"{title}\n{piece}",
                    title=title,
                    url=meta.get("url", ""),
                    provider=meta.get("provider", ""),
                    category=meta.get("category", "general"),
                    meta={"file": str(path.relative_to(sources_dir)), "last_checked": meta.get("last_checked", "")},
                )
            )
    return out
