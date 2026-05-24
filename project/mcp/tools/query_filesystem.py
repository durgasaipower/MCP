"""Tool 2: Query Filesystem - Read/browse documentation files."""

import re
from services.s3_client import read_file, list_files, get_index


def query_filesystem(command: str) -> str:
    """
    Execute a read-only shell-like command against the documentation filesystem.
    Supports: ls, tree, cat, head, tail, find, rg (ripgrep), wc
    """
    command = command.strip()
    parts = command.split()

    if not parts:
        return "Error: empty command"

    cmd = parts[0]

    try:
        if cmd == "ls":
            return _cmd_ls(parts[1:])
        elif cmd == "tree":
            return _cmd_tree(parts[1:])
        elif cmd == "cat":
            return _cmd_cat(parts[1:])
        elif cmd == "head":
            return _cmd_head(parts[1:])
        elif cmd == "tail":
            return _cmd_tail(parts[1:])
        elif cmd == "find":
            return _cmd_find(parts[1:])
        elif cmd == "rg" or cmd == "grep":
            return _cmd_rg(parts[1:])
        elif cmd == "wc":
            return _cmd_wc(parts[1:])
        else:
            return f"Error: unsupported command '{cmd}'. Supported: ls, tree, cat, head, tail, find, rg, wc"
    except Exception as e:
        return f"Error: {str(e)}"


def _cmd_ls(args: list[str]) -> str:
    """List directory contents."""
    path = args[0] if args else "/"
    files = list_files(path)

    # Group into dirs and files
    entries = set()
    for f in files:
        relative = f["path"].removeprefix(path.rstrip("/") + "/")
        if "/" in relative:
            entries.add(relative.split("/")[0] + "/")
        else:
            entries.add(relative)

    return "\n".join(sorted(entries)) if entries else f"(empty directory: {path})"


def _cmd_tree(args: list[str]) -> str:
    """Show directory tree."""
    path = "/"
    depth = 3

    for i, arg in enumerate(args):
        if arg == "-L" and i + 1 < len(args):
            depth = int(args[i + 1])
        elif not arg.startswith("-"):
            path = arg

    files = list_files(path)
    # Build tree output
    lines = [path]
    seen_dirs = set()

    for f in sorted(files, key=lambda x: x["path"]):
        relative = f["path"].removeprefix(path.rstrip("/") + "/")
        parts = relative.split("/")

        if len(parts) > depth:
            continue

        # Add directory entries
        for i in range(len(parts) - 1):
            dir_path = "/".join(parts[: i + 1])
            if dir_path not in seen_dirs:
                seen_dirs.add(dir_path)
                indent = "│   " * i + "├── "
                lines.append(f"{indent}{parts[i]}/")

        # Add file entry
        indent = "│   " * (len(parts) - 1) + "├── "
        lines.append(f"{indent}{parts[-1]}")

    return "\n".join(lines)


def _cmd_cat(args: list[str]) -> str:
    """Read entire file."""
    if not args:
        return "Error: cat requires a file path"
    path = args[0]
    content = read_file(path)
    # Truncate at 30KB
    if len(content) > 30000:
        return content[:30000] + "\n\n[truncated: file too large]"
    return content


def _cmd_head(args: list[str]) -> str:
    """Read first N lines of a file."""
    n = 10
    path = None

    for i, arg in enumerate(args):
        if arg.startswith("-") and arg[1:].isdigit():
            n = int(arg[1:])
        elif not arg.startswith("-"):
            path = arg

    if not path:
        return "Error: head requires a file path"

    content = read_file(path)
    lines = content.split("\n")
    return "\n".join(lines[:n])


def _cmd_tail(args: list[str]) -> str:
    """Read last N lines of a file."""
    n = 10
    path = None

    for i, arg in enumerate(args):
        if arg.startswith("-") and arg[1:].isdigit():
            n = int(arg[1:])
        elif not arg.startswith("-"):
            path = arg

    if not path:
        return "Error: tail requires a file path"

    content = read_file(path)
    lines = content.split("\n")
    return "\n".join(lines[-n:])


def _cmd_find(args: list[str]) -> str:
    """Find files by name pattern."""
    path = "/"
    pattern = "*"

    for i, arg in enumerate(args):
        if arg == "-name" and i + 1 < len(args):
            pattern = args[i + 1].strip("'\"")
        elif not arg.startswith("-"):
            path = arg

    files = list_files(path)
    # Convert glob pattern to regex
    regex = pattern.replace(".", r"\.").replace("*", ".*").replace("?", ".")
    matched = [f["path"] for f in files if re.search(regex, f["path"].split("/")[-1])]
    return "\n".join(matched) if matched else "No files found."


def _cmd_rg(args: list[str]) -> str:
    """Search for pattern in files (simplified ripgrep)."""
    pattern = None
    path = "/"
    case_insensitive = False
    files_only = False

    for i, arg in enumerate(args):
        if arg == "-i":
            case_insensitive = True
        elif arg == "-l":
            files_only = True
        elif arg == "-il" or arg == "-li":
            case_insensitive = True
            files_only = True
        elif not arg.startswith("-") and pattern is None:
            pattern = arg.strip("'\"")
        elif not arg.startswith("-"):
            path = arg

    if not pattern:
        return "Error: rg requires a search pattern"

    flags = re.IGNORECASE if case_insensitive else 0
    files = list_files(path)
    results = []

    for f in files:
        try:
            content = read_file(f["path"])
            if re.search(pattern, content, flags):
                if files_only:
                    results.append(f["path"])
                else:
                    # Show matching lines
                    for line_num, line in enumerate(content.split("\n"), 1):
                        if re.search(pattern, line, flags):
                            results.append(f"{f['path']}:{line_num}:{line.strip()}")
        except Exception:
            continue

    return "\n".join(results[:100]) if results else "No matches found."


def _cmd_wc(args: list[str]) -> str:
    """Count lines, words, characters."""
    if not args:
        return "Error: wc requires a file path"
    path = args[0]
    content = read_file(path)
    lines = content.count("\n") + 1
    words = len(content.split())
    chars = len(content)
    return f"  {lines}  {words}  {chars} {path}"
