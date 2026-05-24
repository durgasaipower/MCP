"""
Test MCP tools directly using the MCP client SDK.
No LLM involved - just raw tool calls.

Usage:
    python test_mcp_client.py
"""

import asyncio
import json
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

MCP_SERVER_URL = "http://localhost:8000/mcp"


async def main():
    async with streamablehttp_client(MCP_SERVER_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected to MCP server!\n")

            # --- List tools ---
            print("=" * 60)
            print("AVAILABLE TOOLS")
            print("=" * 60)
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                print(f"\n  Tool: {tool.name}")
                print(f"  Description: {tool.description[:100]}...")
                print(f"  Schema: {json.dumps(tool.inputSchema, indent=4)}")
            print("\n")

            # --- Test: RAG Search ---
            print("=" * 60)
            print("TEST: search_docs('how to authenticate')")
            print("=" * 60)
            result = await session.call_tool("search_docs", {"query": "how to authenticate"})
            for content in result.content:
                print(content.text)
            print()

            # --- Test: Filesystem - tree ---
            print("=" * 60)
            print("TEST: query_docs_filesystem('tree / -L 2')")
            print("=" * 60)
            result = await session.call_tool("query_docs_filesystem", {"command": "tree / -L 2"})
            for content in result.content:
                print(content.text)
            print()

            # --- Test: Filesystem - ls ---
            print("=" * 60)
            print("TEST: query_docs_filesystem('ls /')")
            print("=" * 60)
            result = await session.call_tool("query_docs_filesystem", {"command": "ls /"})
            for content in result.content:
                print(content.text)
            print()

            # --- Test: Filesystem - cat ---
            print("=" * 60)
            print("TEST: query_docs_filesystem('cat /guides/quickstart.md')")
            print("=" * 60)
            result = await session.call_tool(
                "query_docs_filesystem", {"command": "cat /guides/quickstart.md"}
            )
            for content in result.content:
                print(content.text[:500])
            print()

            # --- Test: Filesystem - rg ---
            print("=" * 60)
            print("TEST: query_docs_filesystem('rg -il \"auth\" /')")
            print("=" * 60)
            result = await session.call_tool(
                "query_docs_filesystem", {"command": 'rg -il "auth" /'}
            )
            for content in result.content:
                print(content.text)

            print("\n" + "=" * 60)
            print("ALL TESTS COMPLETE")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
