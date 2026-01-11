from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple

import numpy as np

try:
    import faiss  # type: ignore
except Exception as e:
    raise RuntimeError("faiss import failed. Install faiss-cpu.") from e

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception as e:
    raise RuntimeError("sentence-transformers import failed. Install sentence-transformers.") from e


KB_DIR = Path("docs/knowledge_base")
ARTIFACT_DIR = Path("artifacts/faiss")
INDEX_PATH = ARTIFACT_DIR / "index.faiss"
CHUNKS_PATH = ARTIFACT_DIR / "chunks.jsonl"


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source_file: str
    section: str
    start_line: int
    end_line: int


def read_text_files(root: Path) -> List[Tuple[Path, str]]:
    files: List[Tuple[Path, str]] = []
    for p in sorted(root.rglob("*.md")):
        txt = p.read_text(encoding="utf-8")
        files.append((p, txt))
    return files


def chunk_markdown(
    text: str,
    source_file: str,
    target_chars: int = 900,
    overlap_chars: int = 120,
) -> List[Chunk]:
    """
    Simple chunker:
    * keeps markdown headers as section labels
    * chunks by character length
    * adds overlap to reduce boundary loss
    """
    lines = text.splitlines()
    chunks: List[Chunk] = []

    current_section = "root"
    buffer: List[str] = []
    buf_start_line = 1
    current_len = 0
    chunk_index = 0

    def flush(end_line: int) -> None:
        nonlocal chunk_index, buffer, current_len, buf_start_line
        if not buffer:
            return
        chunk_text = "\n".join(buffer).strip()
        if chunk_text:
            chunks.append(
                Chunk(
                    chunk_id=f"{source_file}:{chunk_index}",
                    text=chunk_text,
                    source_file=source_file,
                    section=current_section,
                    start_line=buf_start_line,
                    end_line=end_line,
                )
            )
            chunk_index += 1

        buffer = []
        current_len = 0
        buf_start_line = end_line + 1

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            # if header appears and buffer already has content, flush first
            if buffer and current_len >= int(target_chars * 0.6):
                flush(i - 1)
            current_section = stripped.lstrip("#").strip() or "root"

        buffer.append(line)
        current_len += len(line) + 1

        if current_len >= target_chars:
            flush(i)
            # overlap by taking tail of previous content
            if overlap_chars > 0 and i < len(lines):
                overlap: List[str] = []
                running = 0
                j = i
                while j >= 1 and running < overlap_chars:
                    overlap.insert(0, lines[j - 1])
                    running += len(lines[j - 1]) + 1
                    j -= 1
                if overlap:
                    buffer = overlap[:]
                    current_len = sum(len(x) + 1 for x in buffer)
                    buf_start_line = max(1, i - len(buffer) + 1)

    flush(len(lines))

    # remove tiny chunks
    chunks = [c for c in chunks if len(c.text) >= 80]
    return chunks


def build_embeddings(model_name: str, texts: List[str]) -> np.ndarray:
    model = SentenceTransformer(model_name)
    embs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    arr = np.array(embs, dtype=np.float32)
    return arr


def save_chunks_jsonl(chunks: List[Chunk], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            rec: Dict[str, Any] = {
                "chunk_id": c.chunk_id,
                "text": c.text,
                "source_file": c.source_file,
                "section": c.section,
                "start_line": c.start_line,
                "end_line": c.end_line,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def build_faiss_index(embs: np.ndarray) -> Any:
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs)
    return index


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    files = read_text_files(KB_DIR)
    if not files:
        raise RuntimeError(f"No markdown files found under {KB_DIR}")

    all_chunks: List[Chunk] = []
    for path, txt in files:
        rel = str(path.as_posix())
        chunks = chunk_markdown(
            txt,
            source_file=rel,
            target_chars=900,
            overlap_chars=120,
            )
        print(rel, "chunks", len(chunks))
        all_chunks.extend(chunks)


    if not all_chunks:
        raise RuntimeError("Chunking produced zero chunks. Check your docs content.")

    texts = [c.text for c in all_chunks]

    # Default model is local and free to run
    model_name = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")

    embs = build_embeddings(model_name, texts)

    index = build_faiss_index(embs)

    faiss.write_index(index, str(INDEX_PATH))
    save_chunks_jsonl(all_chunks, CHUNKS_PATH)

    print("Knowledge base build complete")
    print(f"Chunks: {len(all_chunks)}")
    print(f"Index: {INDEX_PATH}")
    print(f"Metadata: {CHUNKS_PATH}")
    print(f"Embed model: {model_name}")


if __name__ == "__main__":
    main()
