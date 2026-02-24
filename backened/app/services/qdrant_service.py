from qdrant_client import QdrantClient
from qdrant_client.http.models import models as qmodels
from ..config import QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION
from typing import List, Dict
import uuid
print("aqdrant:",QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION)
_client = None

def get_qdrant():
    global _client
    if _client is None:
        _client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
        _ensure_collection(_client)
    return _client



def _ensure_collection(client: QdrantClient):
    # Get all existing collections
    collections = client.get_collections().collections

    # Check if our collection already exists
    if not any(c.name == QDRANT_COLLECTION for c in collections):
        # Create the collection if missing
        client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=qmodels.VectorParams(
                size=384,  # depends on your embedding model
                distance=qmodels.Distance.COSINE
            )
        )
        client.create_payload_index(
        collection_name=QDRANT_COLLECTION,
        field_name="user_id",
        field_schema=qmodels.PayloadSchemaType.KEYWORD
        )


      
def upsert_chunks(chunks:List[Dict]):
    client = get_qdrant()
    points = []
    
    for ch in chunks:
        pid = str(uuid.uuid4())
        points.append(qmodels.PointStruct(
            id=pid,
            vector=ch["embedding"],
            payload={
                    "text": ch["text"],
                    "source": ch.get("source", ""),
                    "user_id": ch.get("user_id", "global"),
                    "meta": ch.get("meta", {})
                }
        )   )
        client.upsert(collection_name=QDRANT_COLLECTION,points=points)
        

def search(query_embedding,user_id:str,limit:int=12):
    client = get_qdrant()
    
    flt=qmodels.Filter(
    should=[
            qmodels.FieldCondition(key="user_id", match=qmodels.MatchValue(value=user_id)),
            qmodels.FieldCondition(key="user_id", match=qmodels.MatchValue(value="global")),
        ])
    return client.search(collection_name=QDRANT_COLLECTION,
                         query_filter=flt,
                         query_vector=query_embedding,
                         with_payload=True
                        )
    
    
    
    
    