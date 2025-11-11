import re
from typing import List
from ..config import CHUNK_SIZE, CHUNK_OVERLAP

def _split_sentences(text: str) -> List[str]:
    text = re.sub(r'\s+', ' ', text).strip()
    sents = re.split(r'(?<=[.!?])\s+', text)
    return [s for s in sents if s]

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    sents = _split_sentences(text)
    chunks = []
    cur = []
    cur_len = 0
    for s in sents:
        if cur_len + len(s) > chunk_size and cur:
            chunks.append(" ".join(cur).strip())
            # overlap tail
            tail = " ".join(" ".join(cur).split()[-overlap//10:]) if overlap else ""
            cur = [tail] if tail else []
            cur_len = len(tail)
        cur.append(s)
        cur_len += len(s)
    if cur:
        chunks.append(" ".join(cur).strip())
    return [c for c in chunks if c]
