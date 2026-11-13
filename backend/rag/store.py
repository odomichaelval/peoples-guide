"""Local hybrid vector store: numpy cosine similarity + keyword scoring.

Everything lives in data/index/ on the Spark. No external vector DB, nothing to install
on ARM64, and it still works (keyword-only) if the embedding model is not pulled yet.
"""
import json
import math
import re
from collections import Counter
from dataclasses import asdict

import numpy as np

from backend import llm
from backend.config import settings
from backend.rag.documents import Chunk, load_chunks

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = set("the a an and or of to in for on is are be with your you it this that by as at from can if".split())


def tokens(text: str) -> list[str]:
    return [t for t in _TOKEN.findall(text.lower()) if t not in _STOP and len(t) > 1]


class VectorStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self.vectors: np.ndarray | None = None
        self.df: Counter = Counter()
        self.tf: list[Counter] = []

    # ---------- build / persist ----------
    async def build(self, batch: int = 32) -> dict:
        self.chunks = load_chunks(settings.sources_dir)
        self._build_keyword_index()
        vecs: list[list[float]] = []
        embedded = True
        try:
            for i in range(0, len(self.chunks), batch):
                vecs.extend(await llm.embed([c.text for c in self.chunks[i : i + batch]]))
        except llm.LLMError as e:
            print(f"[rag] embeddings unavailable ({e}); index will be keyword-only")
            embedded = False
        self.vectors = self._normalise(np.array(vecs, dtype=np.float32)) if embedded and vecs else None
        self.save()
        return {"chunks": len(self.chunks), "embedded": self.vectors is not None}

    def save(self) -> None:
        settings.index_dir.mkdir(parents=True, exist_ok=True)
        (settings.index_dir / "chunks.json").write_text(json.dumps([asdict(c) for c in self.chunks]))
        if self.vectors is not None:
            np.save(settings.index_dir / "vectors.npy", self.vectors)
        elif (settings.index_dir / "vectors.npy").exists():
            (settings.index_dir / "vectors.npy").unlink()

    def load(self) -> bool:
        f = settings.index_dir / "chunks.json"
        if not f.exists():
            return False
        self.chunks = [Chunk(**c) for c in json.loads(f.read_text())]
        v = settings.index_dir / "vectors.npy"
        self.vectors = np.load(v) if v.exists() else None
        self._build_keyword_index()
        return True

    # ---------- search ----------
    async def search(self, query: str, k: int | None = None) -> list[dict]:
        k = k or settings.rag_top_k
        if not self.chunks:
            return []
        kw = self._keyword_scores(query)
        if kw.max() > 0:
            kw = kw / kw.max()
        score = kw
        if self.vectors is not None:
            try:
                qv = self._normalise(np.array(await llm.embed([query]), dtype=np.float32))[0]
                score = 0.7 * (self.vectors @ qv) + 0.3 * kw
            except llm.LLMError:
                pass
        top = np.argsort(-score)[:k]
        return [
            {**asdict(self.chunks[i]), "score": round(float(score[i]), 4)}
            for i in top
            if score[i] > 0
        ]

    # ---------- helpers ----------
    @staticmethod
    def _normalise(m: np.ndarray) -> np.ndarray:
        n = np.linalg.norm(m, axis=1, keepdims=True)
        n[n == 0] = 1
        return m / n

    def _build_keyword_index(self) -> None:
        self.tf = [Counter(tokens(c.text)) for c in self.chunks]
        self.df = Counter()
        for tf in self.tf:
            self.df.update(tf.keys())

    def _keyword_scores(self, query: str) -> np.ndarray:
        q = tokens(query)
        n = max(len(self.chunks), 1)
        scores = np.zeros(len(self.chunks), dtype=np.float32)
        for i, tf in enumerate(self.tf):
            length = sum(tf.values()) or 1
            s = 0.0
            for t in q:
                if t in tf:
                    idf = math.log(1 + (n - self.df[t] + 0.5) / (self.df[t] + 0.5))
                    s += idf * (tf[t] * 2.2) / (tf[t] + 1.2 * (0.25 + 0.75 * length / 180))
            scores[i] = s
        return scores


store = VectorStore()
