"""Tool 1: RAG Search - Semantic search across documentation."""

from services.vector_db import search


def rag_search(query: str) -> str:
    """
    Search documentation using semantic similarity.
    Returns formatted markdown results with titles, snippets, and paths.
    """
    results = search(query, top_k=5)

    if not results:
        return "No results found for your query."

    output_lines = [f"## Search Results for: \"{query}\"\n"]

    for i, result in enumerate(results, 1):
        similarity_pct = round(result["similarity"] * 100, 1)
        output_lines.append(f"### {i}. {result['title'] or 'Untitled'}")
        output_lines.append(f"**Path:** `{result['source_path']}`")
        output_lines.append(f"**Section:** {result['heading'] or 'N/A'}")
        output_lines.append(f"**Relevance:** {similarity_pct}%\n")
        output_lines.append(result["text"][:500])
        output_lines.append("\n---\n")

    return "\n".join(output_lines)
