import chromadb 
import os 
import uuid 
from datetime import datetime, timezone


from embeddings import embed_text , embed_texts

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR","./chroma_data")
COLLECTION_NAME = "doomscroller-news"

_client = None 
_collection = None 

def get_collection():
    global _client, _collection
    
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        
        _collection = _client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space":"cosine"}
        )
        
    return _collection

def store_article(article:dict):
    collection = get_collection()

    text_to_embed = f"{article['title']}\n{article.get('summary','')}"

    vector = embed_text(text_to_embed)

    vector_id = str(uuid.uuid4())

    metadata = {
        "title": article["title"],
        "summary": article.get("summary", "")[:2000],
        "link": article.get("link", ""),
        "source": article.get("source", ""),
        "stored_at": datetime.now(timezone.utc).isoformat(),
    }

    collection.add(
        ids=[vector_id],
        embeddings=[vector],
        metadatas=[metadata],
        documents=[text_to_embed]
    )
    return vector_id

def store_articles(articles: list[dict]):
    """Embed and store a batch of articles at once (more efficient)."""
    collection = get_collection()
 
    texts = [f"{a['title']}\n{a.get('summary', '')}" for a in articles]
    vectors = embed_texts(texts)
 
    now_iso = datetime.now(timezone.utc).isoformat()
    ids = [str(uuid.uuid4()) for _ in articles]
    metadatas = [
        {
            "title": a["title"],
            "summary": a.get("summary", "")[:2000],
            "link": a.get("link", ""),
            "source": a.get("source", ""),
            "stored_at": now_iso,
        }
        for a in articles
    ]
 
    collection.add(ids=ids, embeddings=vectors, metadatas=metadatas, documents=texts)
    return len(ids)

def find_related_past_article(article_text:str, top_k:int=3, score_threhold:float=0.00):
    
    collection = get_collection()
    query_vector = embed_text(article_text)

    results = collection.query(
        query_embeddings= [query_vector],
        n_results= top_k,
    )

    matches = []

    ids = results.get("ids",[[]])[0]
    distances = results.get("distances",[[]])[0]
    metadatas = results.get("metadatas",[[]])[0]

    for _id, distance, metadata in zip(ids, distances, metadatas):
        similarity = 1 - distance  # convert cosine distance -> similarity

        if similarity >= score_threhold:
            matches.append({"score": similarity, **metadata})
 
    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches
