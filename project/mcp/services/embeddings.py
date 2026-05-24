"""Embedding generation using OpenAI."""

from openai import OpenAI
from config import Config


client = OpenAI(api_key=Config.OPENAI_API_KEY)


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding vector for a text string."""
    response = client.embeddings.create(
        model=Config.EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts."""
    response = client.embeddings.create(
        model=Config.EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]
