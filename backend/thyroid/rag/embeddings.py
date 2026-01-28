"""
OpenAI embeddings integration for RAG pipeline.
"""

from typing import List
import openai
from django.conf import settings


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenAI's embedding model.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not configured in settings")

    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    response = client.embeddings.create(
        model=settings.OPENAI_EMBEDDING_MODEL,
        input=texts
    )

    return [item.embedding for item in response.data]


def get_single_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text string.

    Args:
        text: Text string to embed

    Returns:
        Embedding vector
    """
    embeddings = get_embeddings([text])
    return embeddings[0]
