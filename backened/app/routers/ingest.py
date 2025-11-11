from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import List, Optional
from ..services.scraper import scrape_url
from ..services.chunking import chunk_text
from ..services.embedder import embed_texts
from ..services.qdrant_service import upsert_chunks
from ..schemas import IngestUploadResponse
import pypdf
import chardet

import io
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from starlette.concurrency import run_in_threadpool
from typing import List
import pypdf, chardet

from ..services.chunking import chunk_text
from ..services.embedder import embed_texts
from ..services.qdrant_service import upsert_chunks,QDRANT_COLLECTION
from ..schemas import IngestUploadResponse

router = APIRouter(prefix="/ingest", tags=["ingest"])

@router.post("/url", response_model=IngestUploadResponse)
async def ingest_url(url: str = Form(...), user_id: str = Form("global")):
    text = scrape_url(url)
    if not text:
        raise HTTPException(400, "Could not extract content from URL.")
    chunks = chunk_text(text)
    embs = embed_texts(chunks)
    upsert_chunks([
        {"text": c, "embedding": e, "source": url, "user_id": user_id, "meta": {"type": "url"}}
        for c, e in zip(chunks, embs)
    ])
    return IngestUploadResponse(inserted=len(chunks))

from fastapi import HTTPException, File, Form, APIRouter, UploadFile
from starlette.concurrency import run_in_threadpool
from typing import List
import pypdf
import chardet

# Assume these functions exist and are synchronous
# def chunk_text(text): ...
# def embed_texts(chunks): ...
# def upsert_chunks(data): ...
# class IngestUploadResponse: ...









@router.post("/upload", response_model=IngestUploadResponse)
async def ingest_upload(
    files: List[UploadFile] = File(...),
    user_id: str = Form("global"),
):
    total = 0
    for f in files:
        try:
            content = await f.read()
            print("content:", type(content), len(content))  # Just for debugging

            text = ""
            if f.filename.lower().endswith(".pdf"):
                try:
                    # Wrap bytes in a BytesIO for pypdf
                    pdf_stream = io.BytesIO(content)
                    pdf = await run_in_threadpool(pypdf.PdfReader, pdf_stream)
                    text = "\n".join([page.extract_text() or "" for page in pdf.pages])
                except Exception as e:
                    print("PDF error:", e)
                    raise HTTPException(400, f"Failed to read PDF: {f.filename}")
            else:
                # Detect encoding
                enc_detection = await run_in_threadpool(chardet.detect, content)
                enc = enc_detection.get("encoding") or "utf-8"
                text = content.decode(enc, errors="ignore")

            text = (text or "").strip()
            if not text:
                continue

            # Chunk → embed → upsert
            chunks = await run_in_threadpool(chunk_text, text)
            embs = await run_in_threadpool(embed_texts, chunks)

            await run_in_threadpool(
                upsert_chunks,
                [
                    {
                        "text": c,
                        "embedding": e,
                        "source": f.filename,
                        "user_id": user_id,
                        "meta": {"type": "file"},
                    }
                    for c, e in zip(chunks, embs)
                ],
            )

            total += len(chunks)
        finally:
            await f.close()

    return IngestUploadResponse(inserted=total)
