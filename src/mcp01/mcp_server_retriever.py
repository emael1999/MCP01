
from fastmcp import FastMCP
from typing import Annotated

import os
import json

#import asyncio
#from fastmcp import Client 

from ragcommons.embdbutils import EmbDBTypes
from ragcommons.embfunc import EmbeddingFunctionTypes
from ragcommons.embdbutils import getEmbDBHandle

def load_config(path="config.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)

CONFIG_PATH = os.getenv("MCP_CONFIG_PATH", "config.json")
config = load_config(CONFIG_PATH)

REQUIRED_KEYS = ["server_name", 
                 "tool_description", "tool_name", "tool_tags", 
                 "db_type", "db_host", "db_port", "db_collection",
                 "embedding_function_type","embedding_function_address"]
for key in REQUIRED_KEYS:
    if key not in config:
        raise ValueError(f"Missing required config key: {key}")
    else:
        print(f"[CONFIG] {key}: {config.get(key)}")

SERVER_NAME = config.get("server_name", "Retriever Tools MCP Server")
TOOL_DESCRIPTION = config.get("tool_description", "Default tool description")
TOOL_NAME = config.get("tool_name", "retriever_chunks")
TOOL_TAGS = config.get("tool_tags", ["retrieval", "search", "context", "llm"])

mcp_retriever = FastMCP(name=SERVER_NAME)
   

class MCPRetrieverConfig:
    def __init__(self, 
                db_collection : str,
                embedding_function_address : str,                 
                db_type : EmbDBTypes = EmbDBTypes.chroma,
                db_host : str ='localhost', 
                db_port : int = 8000, 
                embedding_function_type : EmbeddingFunctionTypes 
                                = EmbeddingFunctionTypes.chroma_default
    ):
        self.db_type = db_type
        self.db_host = db_host
        self.db_port = db_port
        self.db_collection = db_collection
        self.embedding_function_type = embedding_function_type        
        self.embedding_function_address = embedding_function_address



class MCPRetriever:
    def __init__(self, config : MCPRetrieverConfig):
        print(f'Inicjujemy {self.__class__.__name__} z parametrami:')
        for conf_field_name, conf_field_value in vars(config).items():
            print(f"{conf_field_name} = {conf_field_value}")
        self.config = None
        self.retriever = None
        self.config = config
        self.initRetriever(config)

    def initRetriever(self, config : MCPRetrieverConfig):
        print("initRetriever start")
        _, _, vector_store = getEmbDBHandle(config.db_type, 
                                            config.db_host, 
                                            config.db_port, 
                                            config.db_collection, 
                                            config.embedding_function_type, 
                                            config.embedding_function_address)
        self.retriever = vector_store.as_retriever()


retrieveConfig = MCPRetrieverConfig(db_type = EmbDBTypes(config.get("db_type", EmbDBTypes.chroma.value)),
                                    db_host = config.get("db_host", 'localhost'), 
                                    db_port = config.get("db_port", 8000), 
                                    db_collection = config.get("db_collection"),
                                    embedding_function_type = EmbeddingFunctionTypes(config.get("embedding_function_type", EmbeddingFunctionTypes.chroma_default.value)),
                                    embedding_function_address = config.get("embedding_function_address"))

retriever = MCPRetriever(retrieveConfig)

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