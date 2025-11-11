from sentence_transformers import SentenceTransformer
from ..config import EMBEDDING_MODEL_NAME

_model = None

def get_embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model

def embed_texts(texts):
    model = get_embedder()
    return model.encode(texts, normalize_embeddings=True, convert_to_numpy=True).tolist()
