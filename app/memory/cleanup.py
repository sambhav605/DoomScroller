from datetime import datetime, timedelta , timezone

from memory.vector_store import get_collection

MEMORY_WINDOW_DAYS = 7 

def delete_old_articles(days=MEMORY_WINDOW_DAYS):
    
    collection = get_collection()

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    all_items = collection.get(include=["metadatas"])

    ids_to_delete = []

    for item_id,metadata in zip(all_items["ids"],all_items['metadatas']):
        stored_at_str = metadata.get("stored_at")

        if not stored_at_str:
            continue 

        stored_at = datetime.fromisoformat(stored_at_str)

        if stored_at< cutoff:
            ids_to_delete.append(item_id)
    
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
    
    return len(ids_to_delete)



