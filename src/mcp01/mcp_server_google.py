
from fastmcp import FastMCP
#import asyncio

import requests
from langchain_google_community import GooglePlacesTool
import os

from fastmcp import Client 

mcp_google = FastMCP(name="Google Tools MCP Server")

@mcp_google.tool()
def google_directions(origin: str, destination: str, mode: str = "driving") -> dict:
    """
    Get travel distance and duration between two locations using Google Directions.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    api_key = os.environ.get('GPLACES_API_KEY')
    if not api_key:
        raise Exception("GPLACES_API_KEY environment variable not set.")
    params = {
        "origin": origin,
        "destination": destination,
        "key": api_key,
        "mode": mode,
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if data["status"] != "OK":
        raise Exception(f"Google API error: {data['status']}")
    leg = data["routes"][0]["legs"][0]
    return {
        "distance_text": leg["distance"]["text"],
        "duration_text": leg["duration"]["text"]
    }

@mcp_google.tool()
def google_places(query: str, location: str = None) -> dict:
    """
    Search for places using Google Places API.
    """
    api_key = os.environ.get('GPLACES_API_KEY')
    if not api_key:
        raise Exception("GPLACES_API_KEY environment variable not set.")
    tool = GooglePlacesTool(api_key=api_key)
    if location:
        query = f"{query} near {location}"
    results = tool.run(query)
    return {"results": results}


if __name__ == "__main__":
    mcp_google.run()


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