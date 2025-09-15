
from fastmcp import FastMCP
from typing import Annotated

#import asyncio
#from fastmcp import Client 

mcp_retriever = FastMCP(name="Retriever Tools MCP Server")

@mcp_retriever.tool(
    name="retriever_chunks",
    description="Retrieve relevant information chunks based on a user's question. Useful for grounding LLM answers with up-to-date context.",
    tags=["retrieval", "search", "question-answering", "context", "llm"],
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