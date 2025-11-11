import google.generativeai as genai
from typing import List
from ..config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are a helpful assistant. Only answer using the provided 'Context' snippets.
If the user's question cannot be answered from the context, clearly say:
"Sorry, this is outside my knowledge base."
Be concise and cite using [n] markers referring to Sources list when relevant.
"""

# from typing import Tuple # If using Python versions older than 3.9

def answer_with_context(query: str, contexts: list[str], citations: list[str]) -> tuple[str, bool]:
    ctx_block = "\n\n".join([f"[{i+1}] {c}" for i, c in enumerate(contexts)]) if contexts else ""
    src_block = "\n".join([f"[{i+1}] {s}" for i, s in enumerate(citations)]) if citations else ""
    prompt = f"""{SYSTEM_PROMPT}

Context:
{ctx_block}

Sources:
{src_block}

User: {query}
Assistant:"""
    model = genai.GenerativeModel(GEMINI_MODEL)
    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()
    from_context = "outside my knowledge base" not in text.lower()
    return text, from_context
