# app/core/gemini_client.py
import logging
from typing import Any, List
import google.generativeai as genai
from app.core.settings import settings

log = logging.getLogger("LearningBuddy.gemini_client")

# configure SDK
if settings.GEMINI_API_KEY:
    try:
        # Mask key for logging
        masked_key = settings.GEMINI_API_KEY[:4] + "..." + settings.GEMINI_API_KEY[-4:]
        log.info(f"Configuring Gemini with API KEY: {masked_key}")
        genai.configure(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        log.error("Failed to configure google.generativeai: %s", e)
else:
    log.error("CRITICAL: GEMINI_API_KEY is missing in settings! Gemini calls will fail.")

EMBED_MODEL = settings.EMBED_MODEL
CHAT_MODEL = settings.GEMINI_CHAT_MODEL

def _extract_embedding(resp: Any) -> List[float]:
    # Many SDK return shapes; normalize to list[float]
    try:
        if isinstance(resp, dict):
            if "embedding" in resp:
                return resp["embedding"]
            if "data" in resp and resp["data"]:
                first = resp["data"][0]
                if isinstance(first, dict) and "embedding" in first:
                    return list(first["embedding"])
        val = getattr(resp, "embedding", None)
        if val is not None:
            if hasattr(val, "values"):
                return list(val.values)
            return list(val)
    except Exception:
        pass
    raise RuntimeError("Unable to extract embedding vector from Gemini response.")

def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    # Try batch embed first
    try:
        resp = genai.embed_content(model=EMBED_MODEL, content=texts)
        emb = _extract_embedding(resp)
        # If it's list-of-lists return as is
        if isinstance(emb, list) and emb and isinstance(emb[0], (list, tuple)):
            return [list(v) for v in emb]
    except Exception as e:
        log.debug("Batch embed attempt failed: %s", e)

    # Fallback: per-item
    out = []
    for t in texts:
        try:
            r = genai.embed_content(model=EMBED_MODEL, content=t)
            out.append(_extract_embedding(r))
        except Exception as e:
            raise RuntimeError(f"embed_texts failed for item: {t[:80]}...: {e}")
    return out

def embed_query(text: str) -> List[float]:
    if not text:
        return []
    try:
        resp = genai.embed_content(model=EMBED_MODEL, content=text)
        return _extract_embedding(resp)
    except Exception as e:
        log.error("embed_query failed: %s", e)
        raise

def generate_answer(prompt: str, max_tokens: int = 512) -> str:
    try:
        # Prefer the GenerativeModel API
        gen = genai.GenerativeModel(CHAT_MODEL)
        resp = gen.generate_content(prompt)
        # many SDK return object with .text
        if hasattr(resp, "text"):
            return resp.text
        # dict-like fallbacks
        if isinstance(resp, dict):
            if "candidates" in resp and resp["candidates"]:
                cand = resp["candidates"][0]
                return cand.get("content") or cand.get("text") or str(cand)
            if "output" in resp:
                return str(resp["output"])
        return str(resp)
    except Exception as e:
        log.error("generate_answer failed: %s", e)
        raise