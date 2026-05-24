"""
Example MCP Server with normal Python functions exposed as tools.

Run with:
    python my_mcp_server.py

This starts an MCP server at http://localhost:8000/mcp
You can connect to it using the MCP client SDK or raw HTTP requests.
"""

from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP(
    name="My Example Server",
    version="1.0.0",
)


# --- Tool 1: Simple calculator ---
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


# --- Tool 2: String utilities ---
@mcp.tool()
def reverse_string(text: str) -> str:
    """Reverse a given string."""
    return text[::-1]


@mcp.tool()
def word_count(text: str) -> dict:
    """Count words, characters, and lines in a text."""
    return {
        "words": len(text.split()),
        "characters": len(text),
        "lines": text.count("\n") + 1,
    }


# --- Tool 3: Data lookup (simulating a database) ---
USERS_DB = {
    "1": {"name": "Alice", "email": "alice@example.com", "role": "admin"},
    "2": {"name": "Bob", "email": "bob@example.com", "role": "developer"},
    "3": {"name": "Charlie", "email": "charlie@example.com", "role": "designer"},
}


@mcp.tool()
def get_user(user_id: str) -> dict:
    """Look up a user by their ID. Returns user info or an error message."""
    user = USERS_DB.get(user_id)
    if user:
        return user
    return {"error": f"User with id '{user_id}' not found"}


@mcp.tool()
def list_users() -> list:
    """List all users in the system."""
    return [{"id": uid, **info} for uid, info in USERS_DB.items()]


# --- Tool 4: Date/time utility ---
@mcp.tool()
def current_time() -> str:
    """Get the current date and time."""
    from datetime import datetime

    return datetime.now().isoformat()


# --- Run the server ---
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
