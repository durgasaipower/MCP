"""
LangGraph Agent with both LOCAL tools and MCP tools.

This example shows how to:
1. Define local tools (normal Python functions)
2. Load remote tools from an MCP server
3. Bind both to a LangGraph ReAct agent

Prerequisites:
    pip install langgraph langchain-openai mcp

    Start the MCP server first:
        python my_mcp_server.py

    Set your OpenAI API key:
        export OPENAI_API_KEY="sk-..."

Run:
    python langgraph_with_mcp.py
"""

import asyncio
import json
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool, StructuredTool
from langgraph.prebuilt import create_react_agent
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession


# ===========================================================================
# LOCAL TOOLS (normal Python functions)
# ===========================================================================

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city. Returns temperature and conditions."""
    # Fake weather data for demo
    weather_data = {
        "new york": "72°F, Sunny",
        "london": "58°F, Cloudy",
        "tokyo": "80°F, Humid",
        "paris": "65°F, Rainy",
    }
    result = weather_data.get(city.lower())
    if result:
        return f"Weather in {city}: {result}"
    return f"Weather data not available for {city}"


@tool
def search_web(query: str) -> str:
    """Search the web for information. Returns a summary of results."""
    # Fake search for demo
    return f"Search results for '{query}': [Simulated result - in production this would call a real search API]"


# ===========================================================================
# MCP TOOLS (loaded from remote MCP server)
# ===========================================================================

async def load_mcp_tools(mcp_url: str) -> list:
    """
    Connect to an MCP server, discover its tools, and convert them
    into LangChain-compatible tool objects.
    """
    mcp_tools = []

    async with streamablehttp_client(mcp_url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Discover all tools from the MCP server
            tools_result = await session.list_tools()

            print(f"Loaded {len(tools_result.tools)} tools from MCP server:")
            for t in tools_result.tools:
                print(f"  - {t.name}: {t.description[:80]}...")

    # For each MCP tool, create a LangChain StructuredTool wrapper
    for mcp_tool in tools_result.tools:
        # Capture tool name in closure
        tool_name = mcp_tool.name
        tool_desc = mcp_tool.description
        tool_schema = mcp_tool.inputSchema

        # Create a wrapper function that calls the MCP server
        def make_mcp_caller(name: str, url: str):
            async def call_mcp_tool(**kwargs) -> str:
                async with streamablehttp_client(url) as (r, w, _):
                    async with ClientSession(r, w) as s:
                        await s.initialize()
                        result = await s.call_tool(name, kwargs)
                        # Extract text content from result
                        texts = [c.text for c in result.content if hasattr(c, "text")]
                        return "\n".join(texts) if texts else str(result.content)
            return call_mcp_tool

        # Build the LangChain tool
        lc_tool = StructuredTool.from_function(
            coroutine=make_mcp_caller(tool_name, mcp_url),
            name=tool_name,
            description=tool_desc,
            args_schema=None,  # Will use the raw schema
        )
        # Override the schema with what MCP provided
        lc_tool.args_schema = None
        mcp_tools.append(lc_tool)

    return mcp_tools


# ===========================================================================
# LANGGRAPH AGENT
# ===========================================================================

async def main():
    MCP_SERVER_URL = "http://localhost:8000/mcp"

    # --- Step 1: Define local tools ---
    local_tools = [get_weather, search_web]
    print("Local tools:")
    for t in local_tools:
        print(f"  - {t.name}: {t.description}")
    print()

    # --- Step 2: Load MCP tools ---
    print("Loading MCP tools...")
    mcp_tools = await load_mcp_tools(MCP_SERVER_URL)
    print()

    # --- Step 3: Combine all tools ---
    all_tools = local_tools + mcp_tools
    print(f"Total tools available to agent: {len(all_tools)}")
    print("-" * 60)
    for t in all_tools:
        print(f"  [{t.name}] {t.description[:60]}")
    print("-" * 60)
    print()

    # --- Step 4: Create LangGraph ReAct agent ---
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    agent = create_react_agent(
        model=llm,
        tools=all_tools,
    )

    # --- Step 5: Run the agent with different queries ---
    queries = [
        "What's the weather in Tokyo?",           # → local tool
        "Add 15 and 27 for me",                   # → MCP tool (add)
        "Reverse the string 'langgraph'",         # → MCP tool (reverse_string)
        "List all users in the system",           # → MCP tool (list_users)
        "What time is it right now?",             # → MCP tool (current_time)
    ]

    for query in queries:
        print(f"\n{'=' * 60}")
        print(f"USER: {query}")
        print("=" * 60)

        result = await agent.ainvoke({"messages": [("user", query)]})

        # Print the final response
        final_message = result["messages"][-1]
        print(f"AGENT: {final_message.content}")


if __name__ == "__main__":
    asyncio.run(main())
