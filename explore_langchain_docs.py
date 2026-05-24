"""
Explore the LangChain MCP docs server - get full structure and read key pages.
Run: python explore_langchain_docs.py
"""

import asyncio
import json
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

MCP_SERVER_URL = "https://docs.langchain.com/mcp"


async def main():
    async with streamablehttp_client(MCP_SERVER_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected!\n")

            # 1. Full directory tree
            print("=" * 80)
            print("FULL DIRECTORY TREE (depth 4)")
            print("=" * 80)
            result = await session.call_tool(
                "query_docs_filesystem_docs_by_lang_chain",
                {"command": "tree / -L 4"}
            )
            tree_output = "\n".join(c.text for c in result.content)
            print(tree_output)

            # 2. Top-level listing
            print("\n" + "=" * 80)
            print("TOP LEVEL: ls /")
            print("=" * 80)
            result = await session.call_tool(
                "query_docs_filesystem_docs_by_lang_chain",
                {"command": "ls /"}
            )
            ls_output = "\n".join(c.text for c in result.content)
            print(ls_output)

            # 3. Count total pages
            print("\n" + "=" * 80)
            print("TOTAL .mdx FILES")
            print("=" * 80)
            result = await session.call_tool(
                "query_docs_filesystem_docs_by_lang_chain",
                {"command": "find / -name '*.mdx' | wc -l"}
            )
            for c in result.content:
                print(c.text)

            # 4. List all .mdx files
            print("\n" + "=" * 80)
            print("ALL .mdx FILES")
            print("=" * 80)
            result = await session.call_tool(
                "query_docs_filesystem_docs_by_lang_chain",
                {"command": "find / -name '*.mdx' | sort"}
            )
            all_files = "\n".join(c.text for c in result.content)
            print(all_files)

            # 5. Read key index/overview pages
            key_pages = [
                "/quickstart.mdx",
                "/tutorials.mdx",
                "/concepts.mdx",
            ]

            for page in key_pages:
                print(f"\n{'=' * 80}")
                print(f"READING: {page} (first 60 lines)")
                print("=" * 80)
                result = await session.call_tool(
                    "query_docs_filesystem_docs_by_lang_chain",
                    {"command": f"head -60 {page}"}
                )
                for c in result.content:
                    print(c.text)

            # Save everything to file
            with open("langchain_docs_full_structure.txt", "w") as f:
                f.write("LangChain Documentation MCP Server - Full Structure\n")
                f.write("=" * 80 + "\n")
                f.write(f"Source: {MCP_SERVER_URL}\n\n")
                f.write("DIRECTORY TREE:\n")
                f.write(tree_output + "\n\n")
                f.write("ALL FILES:\n")
                f.write(all_files + "\n")

            print("\n\nSaved to langchain_docs_full_structure.txt")


if __name__ == "__main__":
    asyncio.run(main())
