"""
src/core/rag.py - the RAG pipeline: Retrieval & Context Injection,
then Generation & Formatting.

This module ONLY answers questions using retrieved context.
It never takes an action.
That's the deliberate RAG-vs-Agentic distinction.
"""

from src.core.vector_store import retrieve
from src.core.llm import chat
from config.settings import settings


BEN10_SYSTEM_PROMPT = getattr(settings, "BEN10_SYSTEM_PROMPT", settings.AURA_SYSTEM_PROMPT)
AURA_SYSTEM_PROMPT = BEN10_SYSTEM_PROMPT
TOP_K = settings.TOP_K


def format_context(chunks):
    """
    Format retrieved chunks with clear source labels.

    This gives the LLM only the retrieved knowledge and helps it
    identify which knowledge type provided the information.
    """

    if not chunks:
        return "No relevant information found in Ben 10's Omnitrix knowledge base."

    lines = []

    for i, c in enumerate(chunks, 1):
        lines.append(
            f"[{i}] (source: {c['doc_type']}) {c['text']}"
        )

    return "\n".join(lines)


def get_doc_type_filter(query):
    """
    Decide whether the query clearly belongs to a specific
    knowledge category.

    Returns the matching doc_type or None when no clear
    category is detected.
    """

    query = query.lower()

    if "project" in query or "projects" in query:
        return "projects"

    if "goal" in query or "goals" in query:
        return "goals"

    if "technology" in query or "technologies" in query:
        return "technologies"

    if "learning" in query or "learn" in query:
        return "learning_journey"

    if "coding style" in query or "coding preference" in query:
        return "coding_preferences"

    return None


def answer(query, top_k=TOP_K, history=None):
    """
    Retrieval & Context Injection -> Generation & Formatting.

    Returns:
        reply: Final LLM response
        chunks: Retrieved chunks used as context
    """

    # 1. Decide whether the query needs a metadata filter
    doc_type_filter = get_doc_type_filter(query)

    # 2. Retrieve relevant chunks from Qdrant
    chunks = retrieve(
        query,
        top_k=top_k,
        doc_type_filter=doc_type_filter,
    )

    # 3. Convert retrieved chunks into LLM-readable context
    context = format_context(chunks)

    # 4. Build the conversation messages
    messages = [
        {
            "role": "system",
            "content": AURA_SYSTEM_PROMPT,
        }
    ]

    # 5. Add previous conversation if available
    if history:
        messages.extend(history)

    # 6. Inject retrieved context + current question
    messages.append(
        {
            "role": "user",
            "content": (
                f"CONTEXT:\n{context}\n\n"
                f"QUESTION: {query}\n\n"
                "Answer using ONLY the context above."
            ),
        }
    )

    # 7. Send everything to the LLM
    reply = chat(messages)

    # 8. Return answer + retrieved evidence
    return reply, chunks