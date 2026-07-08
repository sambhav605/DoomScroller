from pinecone import Pinecone , ServerlessSpec
import os 
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = os.getenv("PINECONE_INDEX_NAME","doomscroller")

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name = index_name,
        dimension= 1024,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    print(f"Created index: {index_name}")
else:
    print(f"Index already exists: {index_name}")
