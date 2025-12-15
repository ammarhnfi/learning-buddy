# generate_vectors.py
from app.utils.vectorstore import build_or_load_vectorstore
from app.utils.data_loader import load_all_data_texts
import logging

logging.basicConfig(level="INFO")
log = logging.getLogger("generate_vectors")

if __name__ == "__main__":
    log.info("Building embeddings (this will call Gemini embed API).")
    texts = load_all_data_texts()
    if not texts:
        log.error("No KB texts found in data/. Make sure CSVs exist and are not empty.")
    else:
        emb, docs = build_or_load_vectorstore(texts, force_rebuild=True)
        log.info("Done. %d vectors generated.", len(docs))