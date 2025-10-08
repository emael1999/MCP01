import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from ragcommons.mcptoolsmanager import MCPToolsManager


async def main():
    servers = [
            "http://127.0.0.1:5003/mcp", 
            "http://127.0.0.1:5004/mcp"
    ]

    #async with MCPToolsManager(servers) as manager:
    manager = MCPToolsManager(servers)
    await manager.setup()
    tools = manager.get_all_tools()
        
    print(f"\nLoaded {len(tools)} tools from {len(servers)} servers.")

    # Create LLM and agent
    llm = ChatOpenAI(temperature=0)
    agent = create_react_agent(llm, tools)

    # Invoke query
    #query = "Find walking distance between Abbey Road Crossing and Buckingham Palace"
    query = "What is there in the heart of Chile?"
    result = await agent.ainvoke({"messages": query})

    # Output response
    final_message = result.get("messages")[-1].content
    print(f"\nAgent response:\n{final_message}")

    await manager.teardown()
    
    
if __name__ == "__main__":
    asyncio.run(main())

