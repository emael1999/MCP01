
from fastmcp import FastMCP
#import asyncio

import requests
from langchain_google_community import GooglePlacesTool
import os

from fastmcp import Client 

mcp_retriever = FastMCP(name="Retriever Tools MCP Server")

@mcp_retriever.tool()
def retriever_chunks(prompt: str) -> dict:
    """
    Retrieve pieces of text that provide up-to-date information 
    to enable a more accurate answer to a given question
    """

    return {
        "result": "Wynik jest pusty"
    }


if __name__ == "__main__":
    mcp_retriever.run()


'''
async def tst():
    print("\n--- Testing Server Locally ---")
    # Point the client directly at the server object
    client = Client(mcp_google)

    # Clients are asynchronous, so use an async context manager
    async with client:
        # Call the 'google_directions' tool
        google_directions_result = await client.call_tool("google_directions", {"origin": "Gdansk", "destination": "Sopot", "mode": "driving"})
        print(f"google_directions result: {google_directions_result}")

asyncio.run(tst())

'''