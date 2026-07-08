import os
import uuid
from datetime import datetime, timezone
import time

from pinecone import Pinecone
from memory.embeddings import embed_text, embed_texts

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "doomscroller")

_pc = None
_index = None


def get_index():
    global _pc, _index
    if _index is None:
        _pc = Pinecone(api_key=PINECONE_API_KEY)
        _index = _pc.Index(INDEX_NAME)
    return _index


def store_article(article: dict):
    index = get_index()

    text_to_embed = f"{article['title']}\n{article.get('summary', '')}"
    vector = embed_text(text_to_embed)
    vector_id = str(uuid.uuid4())

    metadata = {
        "title": article["title"],
        "summary": article.get("summary", "")[:2000],
        "link": article.get("link", ""),
        "source": article.get("source", ""),
        "stored_at": datetime.now(timezone.utc).isoformat(),
        "document": text_to_embed,  # Pinecone has no separate "documents" field, store as metadata
    }

    index.upsert(vectors=[(vector_id, vector, metadata)])
    return vector_id


def store_articles(articles: list[dict], batch_size: int = 20):
    """Embed and store a batch of articles at once (more efficient)."""
    index = get_index()
    now_iso = datetime.now(timezone.utc).isoformat()
    total_stored = 0

    for i in range(0, len(articles), batch_size):
        chunk = articles[i:i + batch_size]
        texts = [f"{a['title']}\n{a.get('summary', '')}" for a in chunk]
        vectors = embed_texts(texts)

        ids = [str(uuid.uuid4()) for _ in chunk]  # fixed: was `articles`, now `chunk`
        metadatas = [
            {
                "title": a["title"],
                "summary": a.get("summary", "")[:2000],
                "link": a.get("link", ""),
                "source": a.get("source", ""),
                "stored_at": now_iso,
                "document": t,
            }
            for a, t in zip(chunk, texts)
        ]

        to_upsert = list(zip(ids, vectors, metadatas))
        index.upsert(vectors=to_upsert)
        total_stored += len(chunk)

        if i + batch_size < len(articles):
            time.sleep(1)

    return total_stored


def find_related_past_article(article_text: str, top_k: int = 3, score_threhold: float = 0.00, max_similarity: float = 0.97):
    index = get_index()
    query_vector = embed_text(article_text)

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
    )

    matches = []
    for match in results.get("matches", []):
        similarity = match["score"]  # Pinecone cosine metric already returns similarity, not distance
        metadata = match.get("metadata", {})

        if score_threhold <= similarity <= max_similarity:
            matches.append({"score": similarity, **metadata})

    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches