import asyncio
from typing import List, Dict

from contextlib import AsyncExitStack

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

from langchain.tools import Tool
from langchain_mcp_adapters.tools import load_mcp_tools

from langgraph.prebuilt import create_react_agent

from langchain_openai import ChatOpenAI





class MCPToolManager:
    def __init__(self, server_urls: List[str]):
        self.server_urls = server_urls
        self.exit_stack = AsyncExitStack()
        self.sessions: Dict[str, ClientSession] = {}
        self.tools_by_server: Dict[str, List[Tool]] = {}

    async def __aenter__(self):
        for url in self.server_urls:
            try:
                client = await self.exit_stack.enter_async_context(streamablehttp_client(url))
                read, write, _ = client

                session = await self.exit_stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                tools = await load_mcp_tools(session)

                self.sessions[url] = session
                self.tools_by_server[url] = tools

            except Exception as e:
                print(f"[Error] Failed to connect to MCP server at {url}: {e}")
                continue

        return self  # returns the manager instance

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.exit_stack.aclose()

    def get_all_tools(self) -> List[Tool]:
        """Return a flat list of all tools from all servers."""
        return [tool for tools in self.tools_by_server.values() for tool in tools]

    def get_tools_by_server(self) -> Dict[str, List[Tool]]:
        """Return a mapping of server URL -> list of tools."""
        return self.tools_by_server

    def get_sessions(self) -> Dict[str, ClientSession]:
        """Return a mapping of server URL -> session (if needed)."""
        return self.sessions


async def main():
    servers = [
            "http://127.0.0.1:5003/mcp", 
            "http://127.0.0.1:5004/mcp"
    ]

    async with MCPToolManager(servers) as manager:
        tools = manager.get_all_tools()
        
        print(f"\nLoaded {len(tools)} tools from {len(servers)} servers.")

        # Create LLM and agent
        llm = ChatOpenAI(temperature=0)
        agent = create_react_agent(llm, tools)

        # Invoke query
        query = "Find walking distance between Abbey Road Crossing and Buckingham Palace"
        result = await agent.ainvoke({"messages": query})

        # Output response
        final_message = result.get("messages")[-1].content
        print(f"\nAgent response:\n{final_message}")
    
    
if __name__ == "__main__":
    asyncio.run(main())

