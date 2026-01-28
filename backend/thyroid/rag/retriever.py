"""
Document retrieval for RAG pipeline.
"""

from typing import List, Dict, Any, Optional
from django.conf import settings
from .vectorstore import get_vectorstore


def retrieve_chunks(
    query: str,
    tr_level: Optional[str] = None,
    action: Optional[str] = None,
    nodule_characteristics: Optional[Dict[str, str]] = None,
    top_k: int = 6,
    relevance_threshold: float = 0.5
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant document chunks for a query.

    Args:
        query: Base query string
        tr_level: TI-RADS classification level
        action: Recommended action (fna, follow_up, no_action)
        nodule_characteristics: Additional nodule features
        top_k: Number of chunks to retrieve
        relevance_threshold: Minimum relevance score (0-1, lower distance is better)

    Returns:
        List of retrieved chunks with metadata
    """
    # Check if OpenAI API key is configured
    if not settings.OPENAI_API_KEY:
        return []

    # Build enhanced query with context
    query_parts = [query]

    if tr_level:
        query_parts.append(f"TI-RADS classification: {tr_level}")

    if action:
        action_terms = {
            'fna': 'fine needle aspiration biopsy FNA cytology',
            'follow_up': 'follow-up surveillance monitoring ultrasound',
            'no_action': 'benign observation no intervention'
        }
        query_parts.append(action_terms.get(action, ''))

    if nodule_characteristics:
        for key, value in nodule_characteristics.items():
            query_parts.append(f"{key}: {value}")

    enhanced_query = " ".join(query_parts)

    # Query vector store
    vectorstore = get_vectorstore()
    results = vectorstore.query(
        query_text=enhanced_query,
        n_results=top_k
    )

    # Format results
    chunks = []
    for i, (doc, metadata, distance) in enumerate(zip(
        results['documents'],
        results['metadatas'],
        results['distances']
    )):
        # Convert distance to relevance score (cosine distance)
        relevance = 1 - distance

        if relevance >= relevance_threshold:
            chunks.append({
                'doc_id': metadata.get('doc_id', 'unknown'),
                'page': metadata.get('page', 0),
                'chunk_id': metadata.get('chunk_id', results['ids'][i]),
                'content': doc,
                'relevance_score': round(relevance, 3),
                'excerpt': doc[:200] + '...' if len(doc) > 200 else doc
            })

    return chunks


def format_chunks_for_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Format retrieved chunks into a context string for LLM.

    Args:
        chunks: List of chunk dictionaries

    Returns:
        Formatted context string
    """
    if not chunks:
        return ""

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = f"[{chunk['doc_id']}, Page {chunk['page']}]"
        context_parts.append(f"Source {i} {source}:\n{chunk['content']}")

    return "\n\n---\n\n".join(context_parts)
