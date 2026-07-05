import os
from dotenv import load_dotenv
from langchain_mistralai import MistralAIEmbeddings

load_dotenv()

MODEL_NAME = "mistral-embed"

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise EnvironmentError(
        "MISTRAL_API_KEY not found. Add it to your .env file"
    )

_embedding_model = None  # lazy singleton so the client is built only once


def get_embedding_model():
    """
    Returns a singleton MistralAIEmbeddings instance that calls
    Mistral's hosted embeddings API.
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = MistralAIEmbeddings(
            model=MODEL_NAME,
            mistral_api_key=MISTRAL_API_KEY,
        )
    return _embedding_model


def embed_text(text: str) -> list[float]:
    """Embed a single piece of text (e.g. one article's title+body)."""
    model = get_embedding_model()
    return model.embed_query(text)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts at once (more efficient than one-by-one)."""
    model = get_embedding_model()
    return model.embed_documents(texts)

