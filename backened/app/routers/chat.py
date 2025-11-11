from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from ..schemas import ChatStartRequest, ChatStartResponse, ChatMessageRequest, ChatMessageResponse, SearchRequest
from ..deps import get_db
from ..models import User, ChatSession, Message
from ..services.embedder import get_embedder
from ..services.retrieval import retrieve
from ..services.llm import answer_with_context
import os


router = APIRouter(prefix="/chat", tags=["chat"])


    
    

@router.post("/start", response_model=ChatStartResponse)
def start_chat(req: ChatStartRequest, db: Session = Depends(get_db)):
    user = db.get(User, req.user_id)
    if not user:
        user = User(id=req.user_id, display_name=req.user_id)
        db.add(user)
        db.commit()
    chat_id = str(uuid4())
    session = ChatSession(id=chat_id, user_id=req.user_id, title=req.title or "New Chat")
    db.add(session)
    db.commit()
    return ChatStartResponse(chat_id=chat_id)

@router.post("/message", response_model=ChatMessageResponse)
def chat_message(req: ChatMessageRequest, db: Session = Depends(get_db)):
    session = db.get(ChatSession, req.chat_id)
    if not session or session.user_id != req.user_id:
        raise HTTPException(404, "Chat session not found.")

    # store user message
    db.add(Message(session_id=session.id, role="user", content=req.message))
    db.commit()

    contexts, cites = retrieve(req.message, user_id=req.user_id, limit=6)
    answer, from_ctx = answer_with_context(req.message, contexts, cites)

    # store assistant message
    db.add(Message(session_id=session.id, role="assistant", content=answer))
    db.commit()

    return ChatMessageResponse(answer=answer, from_context=from_ctx, citations=cites)

# Optional: raw retrieval endpoint (useful for debugging)
@router.post("/search")
def raw_search(req: SearchRequest):
    from ..services.embedder import get_embedder
    from ..services.qdrant_service import search
    q = get_embedder().encode([req.query], normalize_embeddings=True).tolist()[0]
    hits = search(q, user_id=req.user_id, limit=req.top_k)
    return [{"text": h.payload["text"], "source": h.payload.get("source",""), "score": float(h.score)} for h in hits]
