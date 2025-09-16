from fastmcp.client.transports import StreamableHttpTransport
from fastmcp import Client as MCPClient
import asyncio
import json
import jsonschema

from typing import List
from langchain.tools import Tool


async def discover_tools_from_mcp(server_url: str) -> List[Tool]:
    """
    Discover tools from a MCP server using fastmcp.Client (async).
    Validates inputs/outputs with JSON Schema using jsonschema.
    """
    tools = []
    try:
        async with MCPClient(server_url) as client:
            mcp_tools = await client.list_tools()

            for tool_info in mcp_tools:
                name = tool_info.name
                description = tool_info.description or "No description provided."

                # Attributes are named inputSchema and outputSchema
                input_schema = getattr(tool_info, "inputSchema", None)
                output_schema = getattr(tool_info, "outputSchema", None)

                def make_tool_func(client, tool_name, input_schema, output_schema):
                    async def tool_func(input_str: str) -> str:
                        try:
                            # Parse input
                            if input_schema:
                                input_obj = json.loads(input_str)
                                # Validate input against JSON Schema
                                jsonschema.validate(instance=input_obj, schema=input_schema)
                                validated_input = input_obj
                            else:
                                validated_input = input_str  # raw string

                            # Call MCP tool
                            result = await client.call(tool_name, validated_input)

                            # Validate output if schema exists
                            if output_schema:
                                jsonschema.validate(instance=result, schema=output_schema)
                                return json.dumps(result)  # JSON output
                            else:
                                if isinstance(result, (dict, list)):
                                    return json.dumps(result)
                                else:
                                    return str(result)

                        except Exception as e:
                            return f"[Error using tool '{tool_name}']: {e}"

                    return tool_func

                tool_func = make_tool_func(client, name, input_schema, output_schema)

                # Build description with pretty-printed JSON Schema dicts
                description_parts = [description]
                if input_schema:
                    description_parts.append(f"Input schema:\n{json.dumps(input_schema, indent=2)}")
                if output_schema:
                    description_parts.append(f"Output schema:\n{json.dumps(output_schema, indent=2)}")

                tool = Tool(
                    name=name,
                    description="\n".join(description_parts),
                    func=tool_func
                )

                tools.append(tool)

    except Exception as e:
        print(f"[Error] Could not connect to MCP server at {server_url}: {e}")

    return tools


async def  discoverTools(urls : List[str])  -> List[Tool] :
    all_tools = []
    for url in urls:
        tools = await discover_tools_from_mcp(url)
        print(f"✅ Found {len(tools)} tools from {url}")
        all_tools.extend(tools)
    return all_tools



async def interact_with_server() -> List[Tool]:


    urls = [
            "http://127.0.0.1:5003/mcp", 
            "http://127.0.0.1:5004/mcp"
    ]


    all_tools = await discoverTools(urls)

    for tool in all_tools:
        print(f'\nTool:\n{tool}')


if __name__ == "__main__":
    asyncio.run(interact_with_server())        


'''

import asyncio
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

async def main():
    servers = [
            "http://127.0.0.1:5003/mcp", 
            "http://127.0.0.1:5004/mcp"
    ]

    tools = await load_all_tools_from_mcp_servers(servers)

    llm = ChatOpenAI(temperature=0)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    # Example query — must pass JSON input string if tool expects it!
    query = 'Use the "calculator" tool to add: {"a": 5, "b": 7}'
    result = agent.run(query)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())

'''

'''
    print("--- Creating Client ---")
    client = None

    # Option 1: Connect to a server run via `python my_server.py` (uses stdio)
    # client = Client("my_server.py")

    # Option 2: Connect to a server run via `fastmcp run ... --transport sse --port 8080`
    #transport = StreamableHttpTransport(url="http://127.0.0.1:5003/mcp")
    #client = Client(transport)
    client = Client("http://127.0.0.1:5004/mcp")
    

   
    #print(f"Client configured to connect to: {client.target}")

    try:
        async with client:
            
            print("Zaczynamy:\n")
            print(f'Client is connected: {client.is_connected()} \n {client.initialize_result}')
            
            list_tools = await client.list_tools()
            for t in list_tools:
               print(
                    f"Tool:\n"
                    f"Name: {t.name}\n"
                    f"Description: {t.description}\n"
                    f"InputSchema:\n{json.dumps(t.inputSchema, indent=4)}\n"
                    f"OutputSchema:\n{json.dumps(t.outputSchema, indent=4)}"
            )

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("--- Client Interaction Finished ---")

'''
