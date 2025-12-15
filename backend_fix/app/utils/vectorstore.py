# app/utils/vectorstore.py
import json
from pathlib import Path
import numpy as np
from typing import List, Tuple
from app.core.gemini_client import embed_texts
from app.core.settings import settings
import logging

log = logging.getLogger("LearningBuddy.vectorstore")

EMB_DIR = Path(settings.EMB_DIR)
EMB_DIR.mkdir(exist_ok=True, parents=True)
EMB_FILE = EMB_DIR / "kb_embeddings.npy"
TEXT_FILE = EMB_DIR / "kb_texts.json"

def build_or_load_vectorstore(texts: List[str], force_rebuild: bool = False) -> Tuple[np.ndarray, List[str]]:
    if not force_rebuild and EMB_FILE.exists() and TEXT_FILE.exists():
        try:
            log.info("Loading embeddings from disk...")
            arr = np.load(EMB_FILE, allow_pickle=False)
            docs = json.load(open(TEXT_FILE, "r", encoding="utf-8"))
            if not isinstance(arr, np.ndarray) or arr.ndim != 2:
                raise ValueError("Saved embeddings are not 2D array.")
            return arr, docs
        except Exception as e:
            log.warning("Failed loading embeddings: %s. Rebuilding...", e)

    if not texts:
        raise ValueError("No texts to embed.")

    log.info("Generating embeddings via Gemini...")
    vecs = embed_texts(texts)
    arr = np.array(vecs, dtype=float)
    if arr.ndim != 2:
        raise ValueError("Embedding error: vectors are not 2D.")
    np.save(EMB_FILE, arr)
    json.dump(texts, open(TEXT_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return arr, texts