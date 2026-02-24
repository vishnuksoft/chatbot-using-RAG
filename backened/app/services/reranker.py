from typing import List, Dict
from sentence_transformers import CrossEncoder
from ..config import RERANK_MODEL_NAME

_ce = None

def get_reranker():
    global _ce
    if _ce is None:
        _ce = CrossEncoder(RERANK_MODEL_NAME)
    return _ce

def rerank(query: str, hits: List[Dict], top_k: int = 6):
    ce = get_reranker()
    pairs = [(query, h.payload["text"]) for h in hits]
    if not pairs:
        return []
    scores = ce.predict(pairs)
    with_scores = list(zip(hits, scores))
    with_scores.sort(key=lambda x: float(x[1]), reverse=True)
    return [h for (h, s) in with_scores[:top_k]]

