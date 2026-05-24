"""
Test MCP tools with an LLM (LangGraph ReAct agent).
The LLM decides which tool to call based on the user's question.

Usage:
    export OPENAI_API_KEY="sk-..."
    python test_with_llm.py
"""

import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

MCP_SERVER_URL = "http://localhost:8000/mcp"


async def load_mcp_tools(url: str) -> list:
    """Load tools from MCP server and wrap as LangChain tools."""
    tools = []

    async with streamablehttp_client(url) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            tools_result = await session.list_tools()

    for mcp_tool in tools_result.tools:
        tool_name = mcp_tool.name
        tool_desc = mcp_tool.description

        def make_caller(name: str):
            async def call(**kwargs) -> str:
                async with streamablehttp_client(url) as (r, w, _):
                    async with ClientSession(r, w) as s:
                        await s.initialize()
                        result = await s.call_tool(name, kwargs)
                        texts = [c.text for c in result.content if hasattr(c, "text")]
                        return "\n".join(texts) if texts else str(result.content)
            return call

        lc_tool = StructuredTool.from_function(
            coroutine=make_caller(tool_name),
            name=tool_name,
            description=tool_desc,
        )
        tools.append(lc_tool)

    return tools


async def main():
    print("Loading MCP tools...")
    tools = await load_mcp_tools(MCP_SERVER_URL)
    print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}\n")

    # Create LangGraph agent
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent = create_react_agent(model=llm, tools=tools)

    # Test queries
    queries = [
        "How do I authenticate with the API?",
        "Show me the directory structure of the docs",
        "Read the quickstart guide",
        "Find all files that mention 'vector search'",
    ]

    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"USER: {query}")
        print("=" * 60)

        result = await agent.ainvoke({"messages": [("user", query)]})
        final = result["messages"][-1]
        print(f"AGENT: {final.content[:500]}")


if __name__ == "__main__":
    asyncio.run(main())
