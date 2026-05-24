"""
MCP Server with RAG Search + Filesystem tools + Upload endpoint.

Run:
    python server.py

Endpoints:
    POST /mcp       → MCP protocol (tools/call, tools/list, etc.)
    POST /upload    → REST file upload
    GET  /health    → Health check
"""

from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from config import Config
from tools.rag_search import rag_search
from tools.query_filesystem import query_filesystem
from services.s3_client import upload_file, update_index


# --- MCP Server ---
mcp = FastMCP(
    name="Docs MCP Server",
    version="1.0.0",
)


@mcp.tool()
def search_docs(query: str) -> str:
    """
    Search across the documentation knowledge base using semantic similarity.
    Returns relevant chunks with titles, snippets, and file paths.
    Use this for broad questions like "how to authenticate" or "rate limiting".
    """
    return rag_search(query)


@mcp.tool()
def query_docs_filesystem(command: str) -> str:
    """
    Run a read-only shell command against the documentation filesystem.
    Supports: ls, tree, cat, head, tail, find, rg (ripgrep), wc.
    Use this to read specific pages, explore structure, or do exact keyword search.

    Examples:
        tree / -L 2
        cat /guides/quickstart.md
        head -50 /api-reference/endpoints.md
        rg -il "authentication" /
        find / -name "*.md"
    """
    return query_filesystem(command)


# --- REST Upload Endpoint ---
async def handle_upload(request: Request) -> JSONResponse:
    """Handle file upload via REST (not MCP)."""
    # Auth check
    api_key = request.headers.get("X-API-Key")
    if api_key != Config.UPLOAD_API_KEY:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    # Parse multipart form
    form = await request.form()
    file = form.get("file")
    path = form.get("path")
    title = form.get("title", "")

    if not file or not path:
        return JSONResponse(
            {"error": "Missing required fields: file, path"},
            status_code=400,
        )

    # Read file content
    content = await file.read()

    # Upload to S3
    s3_key = upload_file(content, path)

    # Update index
    update_index(path, title or path.split("/")[-1], len(content))

    return JSONResponse({
        "status": "uploaded",
        "path": path,
        "s3_key": s3_key,
        "message": "File uploaded. Indexing will complete in ~30 seconds.",
    })


async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "healthy", "service": "docs-mcp-server"})


# --- Combined App ---
# Mount REST routes alongside MCP
rest_app = Starlette(
    routes=[
        Route("/upload", handle_upload, methods=["POST"]),
        Route("/health", health_check, methods=["GET"]),
    ]
)


if __name__ == "__main__":
    # Run MCP server (handles /mcp endpoint)
    # For production, mount rest_app alongside mcp using a shared ASGI app
    mcp.run(transport="streamable-http", host=Config.HOST, port=Config.PORT)
