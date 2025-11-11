# Chatbot Using RAG

This is a Retrieval-Augmented Generation chatbot built with FastAPI, Qdrant, and Gemini.  
It supports:
- PDF / TXT file ingestion
- URL scraping and embedding
- Reranked retrieval
- User-based chat history

## Run Locally
```bash
cd rg_qdrant
cd backened
uvicorn app.main:app --reload --port 8000

just live frontend html file to get frontend view
