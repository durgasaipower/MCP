"""Document chunking logic."""

import re


def chunk_document(
    text: str,
    source_path: str,
    title: str = "",
    max_chunk_size: int = 1000,
    overlap: int = 100,
) -> list[dict]:
    """
    Chunk a document into segments.
    Strategy: Split by headings first, then by size if sections are too large.
    """
    # Split by markdown headings (## or ###)
    sections = _split_by_headings(text)

    chunks = []
    chunk_index = 0

    for heading, section_text in sections:
        # If section fits in one chunk, keep it whole
        if len(section_text.split()) <= max_chunk_size:
            chunks.append({
                "text": section_text.strip(),
                "source_path": source_path,
                "title": title,
                "heading": heading,
                "chunk_index": chunk_index,
            })
            chunk_index += 1
        else:
            # Split large sections into overlapping chunks
            sub_chunks = _split_by_size(section_text, max_chunk_size, overlap)
            for sub in sub_chunks:
                chunks.append({
                    "text": sub.strip(),
                    "source_path": source_path,
                    "title": title,
                    "heading": heading,
                    "chunk_index": chunk_index,
                })
                chunk_index += 1

    return chunks


def _split_by_headings(text: str) -> list[tuple[str, str]]:
    """Split text by markdown headings. Returns [(heading, content), ...]."""
    # Match ## or ### headings
    pattern = r"^(#{2,3})\s+(.+)$"
    lines = text.split("\n")

    sections = []
    current_heading = ""
    current_lines = []

    for line in lines:
        match = re.match(pattern, line)
        if match:
            # Save previous section
            if current_lines:
                sections.append((current_heading, "\n".join(current_lines)))
            current_heading = match.group(2)
            current_lines = [line]
        else:
            current_lines.append(line)

    # Don't forget the last section
    if current_lines:
        sections.append((current_heading, "\n".join(current_lines)))

    return sections if sections else [("", text)]


def _split_by_size(text: str, max_words: int, overlap_words: int) -> list[str]:
    """Split text into chunks of max_words with overlap."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + max_words
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap_words

    return chunks
