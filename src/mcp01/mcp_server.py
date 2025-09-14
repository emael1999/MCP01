from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List, Dict, Any
import os
import requests
import json

# Import GooglePlacesTool from langchain-google-community
from langchain_google_community import GooglePlacesTool

# --- Models matching toolgoogledirect.py ---
class ModeEnum(str, Enum):
    driving = "driving"
    walking = "walking"
    bicycling = "bicycling"
    transit = "transit"

class RoutingInput(BaseModel):
    origin: str = Field(..., description="Start location")
    destination: str = Field(..., description="Destination location")
    mode: ModeEnum = Field(default=ModeEnum.driving, description="Mode of travel")

class RoutingOutput(BaseModel):
    distance_text: str
    duration_text: str
    #polyline: Optional[str]

# --- Google Places Models ---
class GooglePlacesInput(BaseModel):
    query: str = Field(..., description="Search query for Google Places")
    location: Optional[str] = Field(None, description="Location for the search (optional)")

class GooglePlacesOutput(BaseModel):
    results: str

# --- MCP Tool Metadata Model ---
class MCPToolDescription(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

# --- FastAPI app ---
app = FastAPI(
    title="MCP Server",
    description="MCP-enabled server exposing tools for LLM/agent use.",
    version="1.0.0"
)

@app.post("/google_directions", response_model=RoutingOutput, tags=["tools"])
def google_directions_endpoint(inputs: RoutingInput):
    """
    Calls the Google Directions API to get travel distance and duration.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    api_key = os.environ.get('GPLACES_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="GPLACES_API_KEY environment variable not set.")
    params = {
        "origin": inputs.origin,
        "destination": inputs.destination,
        "key": api_key,
        "mode": inputs.mode or "driving",
    }
    print(f'Parametry do google_directions: \n {params}')
    resp = requests.get(url, params=params)
    data = resp.json()
    if data["status"] != "OK":
        raise HTTPException(status_code=400, detail=f"Google API error: {data['status']}")
    leg = data["routes"][0]["legs"][0]
    print(f'google_routes: \n{json.dumps(data, indent=2)}')
    return RoutingOutput(
        distance_text=leg["distance"]["text"],
        duration_text=leg["duration"]["text"]
    )

@app.post("/google_places", response_model=GooglePlacesOutput, tags=["tools"])
def google_places_endpoint(inputs: GooglePlacesInput):
    """
    Uses Google Places API to search for places matching a query.
    """
    api_key = os.environ.get('GPLACES_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="GPLACES_API_KEY environment variable not set.")
    tool = GooglePlacesTool(api_key=api_key)
    try:
        query = inputs.query
        if inputs.location:
            query += f" near {inputs.location}"
        print(f'Zapytanie do Google Places {query}')
        results = tool.run(query)
        return GooglePlacesOutput(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- MCP Features: Tool Discovery Endpoint ---
@app.get("/mcp/tools", response_model=List[MCPToolDescription], tags=["mcp"])
def list_tools():
    """
    Lists all tools exposed by this MCP server, with input/output schemas.
    """
    # Tool metadata
    tools = [
        MCPToolDescription(
            name="google_directions",
            description="Get travel distance and duration between two locations using Google Directions.",
            input_schema=RoutingInput.schema(),
            output_schema=RoutingOutput.schema()
        ),
        MCPToolDescription(
            name="google_places",
            description="Search for places using Google Places API.",
            input_schema=GooglePlacesInput.schema(),
            output_schema=GooglePlacesOutput.schema()
        ),
    ]
    return tools

# --- MCP Features: Tool Prompt Endpoint ---
@app.get("/mcp/prompt", tags=["mcp"])
def get_mcp_prompt():
    """
    Returns a system prompt describing available tools and their usage for LLMs/agents.
    """
    prompt = (
        "You can answer questions directly or use one of these tools:\n"
        "1. google_directions: Get directions between two places.\n"
        "   Input: {\"origin\": \"string\", \"destination\": \"string\", \"mode\": \"driving|walking|bicycling|transit\"}\n"
        "2. google_places: Search for places.\n"
        "   Input: {\"query\": \"string\", \"location\": \"string (optional)\"}\n"
        "If you need to use a tool, respond ONLY with:\n"
        "TOOL_CALL: <tool_name> <JSON input>\n"
        "Otherwise, answer normally."
    )
    return {"prompt": prompt}

# To run: uvicorn mcp_server:app --reload
