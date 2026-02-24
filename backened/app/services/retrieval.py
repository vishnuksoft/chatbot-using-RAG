from typing import List,Tuple
from .embedder import get_embedder
from .qdrant_service import search
from .reranker import rerank

def retrieve(query: str, user_id: str, limit: int = 6) -> Tuple[List[str], List[str]]:
    # Embed query
    qvec = get_embedder().encode([query], normalize_embeddings=True).tolist()[0]
    # ANN
    hits = search(qvec, user_id=user_id, limit=12)
    # Rerank
    reranked = rerank(query, hits, top_k=limit)
    contexts = [h.payload["text"] for h in reranked]
    cites = [h.payload.get("source", "") for h in reranked]
    return contexts, cites