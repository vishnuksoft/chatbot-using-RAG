from pydantic import BaseModel, Field
from typing import List, Optional

class IngestURLRequest(BaseModel):
    url: str
    meta: Optional[dict] = None

class IngestUploadResponse(BaseModel):
    inserted: int

class SearchRequest(BaseModel):
    query: str
    user_id: str
    top_k: int = 6

class ChatStartRequest(BaseModel):
    user_id: str
    title: Optional[str] = None

class ChatStartResponse(BaseModel):
    chat_id: str

class ChatMessageRequest(BaseModel):
    user_id: str
    chat_id: str
    message: str

class ChatMessageResponse(BaseModel):
    answer: str
    from_context: bool
    citations: List[str] = Field(default_factory=list)  # list of source URLs or document ids

