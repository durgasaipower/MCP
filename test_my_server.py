"""
Test script to connect to my_mcp_server.py using the MCP client SDK.

Prerequisites:
    1. Start the server first: python my_mcp_server.py
    2. Then run this:         python test_my_server.py
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

            # --- List all tools ---
            print("=" * 60)
            print("AVAILABLE TOOLS")
            print("=" * 60)
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                print(f"\n  Tool: {tool.name}")
                print(f"  Description: {tool.description}")
                print(f"  Input Schema: {json.dumps(tool.inputSchema, indent=4)}")
            print("\n")

            # --- Call: add ---
            print("=" * 60)
            print("TEST: add(5, 3)")
            print("=" * 60)
            result = await session.call_tool("add", {"a": 5, "b": 3})
            for content in result.content:
                print(f"  Result: {content.text}")
            print()

            # --- Call: multiply ---
            print("=" * 60)
            print("TEST: multiply(7, 6)")
            print("=" * 60)
            result = await session.call_tool("multiply", {"a": 7, "b": 6})
            for content in result.content:
                print(f"  Result: {content.text}")
            print()

            # --- Call: reverse_string ---
            print("=" * 60)
            print("TEST: reverse_string('hello world')")
            print("=" * 60)
            result = await session.call_tool("reverse_string", {"text": "hello world"})
            for content in result.content:
                print(f"  Result: {content.text}")
            print()

            # --- Call: word_count ---
            print("=" * 60)
            print("TEST: word_count('MCP is a protocol for AI tools')")
            print("=" * 60)
            result = await session.call_tool("word_count", {"text": "MCP is a protocol for AI tools"})
            for content in result.content:
                print(f"  Result: {content.text}")
            print()

            # --- Call: list_users ---
            print("=" * 60)
            print("TEST: list_users()")
            print("=" * 60)
            result = await session.call_tool("list_users", {})
            for content in result.content:
                print(f"  Result: {content.text}")
            print()

            # --- Call: get_user ---
            print("=" * 60)
            print("TEST: get_user('2')")
            print("=" * 60)
            result = await session.call_tool("get_user", {"user_id": "2"})
            for content in result.content:
                print(f"  Result: {content.text}")
            print()

            # --- Call: get_user (not found) ---
            print("=" * 60)
            print("TEST: get_user('99') - should return error")
            print("=" * 60)
            result = await session.call_tool("get_user", {"user_id": "99"})
            for content in result.content:
                print(f"  Result: {content.text}")
            print()

            # --- Call: current_time ---
            print("=" * 60)
            print("TEST: current_time()")
            print("=" * 60)
            result = await session.call_tool("current_time", {})
            for content in result.content:
                print(f"  Result: {content.text}")
            print()

            print("=" * 60)
            print("ALL TESTS COMPLETE")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
