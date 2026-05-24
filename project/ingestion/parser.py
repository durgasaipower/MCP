"""File format parser - extract text and title from different formats."""

import re


def parse_file(content: str, filename: str) -> tuple[str, str]:
    """
    Parse file content and extract title + body text.
    Returns: (title, text)
    """
    if filename.endswith((".md", ".mdx")):
        return _parse_markdown(content)
    elif filename.endswith(".txt"):
        return _parse_text(content)
    else:
        # Default: treat as plain text
        return _parse_text(content)


def _parse_markdown(content: str) -> tuple[str, str]:
    """Parse markdown file. Extract title from frontmatter or first heading."""
    title = ""
    text = content

    # Check for YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            text = parts[2].strip()

            # Extract title from frontmatter
            title_match = re.search(r"^title:\s*[\"']?(.+?)[\"']?\s*$", frontmatter, re.MULTILINE)
            if title_match:
                title = title_match.group(1)

    # If no title from frontmatter, use first # heading
    if not title:
        heading_match = re.match(r"^#\s+(.+)$", text, re.MULTILINE)
        if heading_match:
            title = heading_match.group(1)

    return title, text


def _parse_text(content: str) -> tuple[str, str]:
    """Parse plain text file. Use first line as title."""
    lines = content.strip().split("\n")
    title = lines[0].strip() if lines else ""
    return title, content
