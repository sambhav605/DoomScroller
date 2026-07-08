from datetime import datetime, timedelta, timezone

from memory.vector_store import get_index

MEMORY_WINDOW_DAYS = 7


def delete_old_articles(days=MEMORY_WINDOW_DAYS):
    index = get_index()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    
    stats = index.describe_index_stats()
    total_vectors = stats.get("total_vector_count", 0)

    if total_vectors == 0:
        return 0

    dummy_vector = [0.0] * stats["dimension"]
    results = index.query(
        vector=dummy_vector,
        top_k=min(total_vectors, 10000),  # Pinecone caps top_k at 10,000
        include_metadata=True,
    )

    ids_to_delete = []
    for match in results.get("matches", []):
        stored_at_str = match.get("metadata", {}).get("stored_at")
        if not stored_at_str:
            continue

        stored_at = datetime.fromisoformat(stored_at_str)
        if stored_at < cutoff:
            ids_to_delete.append(match["id"])

    if ids_to_delete:
        index.delete(ids=ids_to_delete)

    return len(ids_to_delete)