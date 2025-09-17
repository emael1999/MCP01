
from fastmcp import FastMCP
from typing import Annotated

import requests
from langchain_google_community import GooglePlacesTool
import os

import asyncio
from fastmcp import Client 

import json

# Your FastMCP server instance
mcp_google = FastMCP(name="Google Maps MCP Server")

@mcp_google.tool(
    name="google_places",
    description="Search for places using the Google Places API, optionally near a specific location.",
    tags=["maps", "places", "google", "location", "search", "points-of-interest"],
    annotations={"read_only": True},
    output_schema={
        "type": "object",
        "properties": {
            "results": {
                "type": "string",
                "description": "Text description of the places found matching the query"
            }
        },
        "required": ["results"]
    }
)
def google_places(
    query: Annotated[str, "What type of place you're searching for (e.g., 'coffee shops', 'bookstores')"],
    location: Annotated[str, "Optional location to search near (e.g., 'New York', 'Paris')"] = None
) -> dict:
    """
    Search for places using the Google Places API.
    If a location is provided, results will be scoped to that area.
    """
    api_key = os.environ.get("GPLACES_API_KEY")
    if not api_key:
        raise Exception("GPLACES_API_KEY environment variable not set.")

    tool = GooglePlacesTool(api_key=api_key)
    full_query = f"{query} near {location}" if location else query
    results = tool.run(full_query)

    return {"results": results}

@mcp_google.tool(
    name="google_directions",
    description="Get estimated travel distance and time between two locations using the Google Maps Directions API.",
    tags=["maps", "google", "directions", "navigation", "travel", "distance"],
    annotations={"read_only": True},
    output_schema={
        "type": "object",
        "properties": {
            "distance_text": {
                "type": "string",
                "description": "Human-readable distance (e.g., '5.4 km')"
            },
            "duration_text": {
                "type": "string",
                "description": "Estimated travel time (e.g., '12 mins')"
            }
        },
        "required": ["distance_text", "duration_text"]
    }
)
def google_directions(
    origin: Annotated[str, "The starting location (address or place name)"],
    destination: Annotated[str, "The destination location (address or place name)"],
    mode: Annotated[str, "Transportation mode: 'driving', 'walking', 'bicycling', or 'transit'"] = "driving"
) -> dict:
    """
    Uses the Google Maps Directions API to retrieve the estimated distance and travel time
    between two locations using a specified mode of transportation.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    api_key = os.environ.get('GPLACES_API_KEY')
    if not api_key:
        raise Exception("GPLACES_API_KEY environment variable not set.")

    params = {
        "origin": origin,
        "destination": destination,
        "key": api_key,
        "mode": mode
    }

    print(f'google_directions: \n{params}')

    response = requests.get(url, params=params)

    data = response.json()
    
    print(f'Response data:\n{json.dumps(data, indent=4)}')

    if data["status"] != "OK":
        raise Exception(f"Google API error: {data['status']}")

    leg = data["routes"][0]["legs"][0]
    return {
        "distance_text": leg["distance"]["text"],
        "duration_text": leg["duration"]["text"]
    }


''''''
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