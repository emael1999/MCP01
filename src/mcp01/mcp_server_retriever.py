
from fastmcp import FastMCP
from typing import Annotated

import os
import json

#import asyncio
#from fastmcp import Client 

def load_config(path="config.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)

CONFIG_PATH = os.getenv("MCP_CONFIG_PATH", "config.json")
config = load_config(CONFIG_PATH)

TOOL_DESCRIPTION = config.get("description", "Default tool description.")
TOOL_NAME = config.get("tool_name", "retriever_chunks")
TOOL_TAGS = config.get("tool_tags", ["retrieval", "search", "context", "llm"])
DB_HOST = config.get("db_host", "localhost")  # <- This is your new config parameter

REQUIRED_KEYS = ["description", "tool_name", "tool_tags", "db_host"]
for key in REQUIRED_KEYS:
    if key not in config:
        raise ValueError(f"Missing required config key: {key}")
    else:
        print(f"[CONFIG] {key}: {config.get(key)}")


mcp_retriever = FastMCP(name="Retriever Tools MCP Server")

@mcp_retriever.tool(
    name=TOOL_NAME,
    description=TOOL_DESCRIPTION,
    tags=TOOL_TAGS,
    annotations={"read_only": True},
    output_schema={
        "type": "object",
        "properties": {
            "result": {
                "type": "string",
                "description": "Concatenated or formatted chunks of retrieved context relevant to the prompt"
            }
        },
        "required": ["result"]
    }
)
def retriever_chunks(
    prompt: Annotated[str, "The user's question or query needing additional contextual information"]
) -> dict:
    return {
        "result": "Wynik jest pusty"
    }


if __name__ == "__main__":
    mcp_retriever.run()


'''
async def tst():
    print("\n--- Testing Server Locally ---")
    # Point the client directly at the server object
    client = Client(mcp_retriever)

    # Clients are asynchronous, so use an async context manager
    async with client:
        # Call the 'google_directions' tool
        result = await client.call_tool("retriever_chunks", {"prompt": "What is love?"})
        print(f"retriever_chunks result: {result}")

asyncio.run(tst())
'''