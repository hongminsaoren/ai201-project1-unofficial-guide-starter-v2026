"""Stage 2: paragraph-aware campus chunks with repeated title context.

`split_documents` is the Unit 1 custom chunker. `fallback_split` preserves
fixed-window behavior for comparisons in Unit 2; pass 800 and 120 explicitly
to reproduce the original starter settings.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = config.CHUNK_OVERLAP if overlap is None else overlap

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def split_documents(documents: list[Document]) -> list[Chunk]:
    """Keep short posts whole; split longer bodies at complete thought boundaries.

    CHUNK_SIZE is a soft body budget. Titles repeat as context. Body overlap
    is zero. A single over-budget sentence stays whole to avoid losing meaning.
    """
    import re

    if config.CHUNK_SIZE <= 0:
        raise ValueError("CHUNK_SIZE must be positive")
    if config.CHUNK_OVERLAP != 0:
        raise ValueError("This paragraph chunker uses zero body overlap")
    chunks: list[Chunk] = []
    for doc in documents:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", doc.text) if p.strip()]
        if not paragraphs:
            continue
        # Supplied campus posts start with a short, standalone title.
        has_title = len(paragraphs) > 1 and "\n" not in paragraphs[0] and len(paragraphs[0]) <= 100
        title = paragraphs[0] if has_title else ""
        body = paragraphs[1:] if has_title else paragraphs
        units = []
        for paragraph in body:
            if len(paragraph) <= config.CHUNK_SIZE:
                units.append(paragraph)
            else:
                units.extend(re.split(r'(?<=[.!?])\s+(?=[A-Z"“])', paragraph))
        batches = []
        current = ""
        for unit in units:
            proposed = current + "\n\n" + unit if current else unit
            if current and len(proposed) > config.CHUNK_SIZE:
                batches.append(current)
                current = unit
            else:
                current = proposed
        if current:
            batches.append(current)
        for index, body_text in enumerate(batches):
            text = f"{title}\n\n{body_text}" if title else body_text
            chunks.append(Chunk(text, doc.source, index, "chunker.py::split_documents"))
    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
