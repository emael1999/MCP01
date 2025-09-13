from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
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

# --- FastAPI app ---
app = FastAPI()

@app.post("/google_directions", response_model=RoutingOutput)
def google_directions_endpoint(inputs: RoutingInput):
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

@app.post("/google_places", response_model=GooglePlacesOutput)
def google_places_endpoint(inputs: GooglePlacesInput):
    api_key = os.environ.get('GPLACES_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail="GPLACES_API_KEY environment variable not set.")
    tool = GooglePlacesTool(api_key=api_key)
    try:
        query = inputs.query
        if inputs.location:
            query += f" near {inputs.location}"
        # The tool's run method expects a string query
        print(f'Zapytanie do Google Places {query}')
        results = tool.run(query)
        return GooglePlacesOutput(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To run: uvicorn mcp_server:app --reload
