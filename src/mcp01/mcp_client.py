from fastmcp.client.transports import StreamableHttpTransport
from fastmcp import Client
import asyncio

async def interact_with_server():
    print("--- Creating Client ---")
    client = None

    # Option 1: Connect to a server run via `python my_server.py` (uses stdio)
    # client = Client("my_server.py")

    # Option 2: Connect to a server run via `fastmcp run ... --transport sse --port 8080`
    #transport = StreamableHttpTransport(url="http://127.0.0.1:5003/mcp")
    #client = Client(transport)
    client = Client("http://127.0.0.1:5003/mcp")
    

   
    #print(f"Client configured to connect to: {client.target}")

    try:
        async with client:
            
            print("Zaczynamy:\n")
            print(f'Client is connected: {client.is_connected()} \n {client.initialize_result}')
            
            list_tools = await client.list_tools()
            print(f'List tools: \n {list_tools}\n')
            
            #list_tools_mcp = await client.list_tools_mcp()
            #print (f'List Tools mcp: \n {list_tools_mcp}\n')

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("--- Client Interaction Finished ---")

if __name__ == "__main__":
    asyncio.run(interact_with_server())