from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
import os
import requests
import json

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

# --- FastAPI app ---
app = FastAPI()

@app.post("/google_directions", response_model=RoutingOutput)
def google_directions_endpoint(inputs: RoutingInput):
    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": inputs.origin,
        "destination": inputs.destination,
        "key": os.environ.get('GPLACES_API_KEY'),
        "mode": inputs.mode or "driving",
    }

    print(f'params: \n {params}')

    resp = requests.get(url, params=params)
    data = resp.json()
    if data["status"] != "OK":
        raise HTTPException(status_code=400, detail=f"Google API error: {data['status']}")
    leg = data["routes"][0]["legs"][0]

    print(f'google_routes: \n{json.dumps(data, indent=2)}')

    return RoutingOutput(
        distance_text=leg["distance"]["text"],
        duration_text=leg["duration"]["text"]
        #,polyline=data["routes"][0].get("overview_polyline", {}).get("points", None)
    )

# To run: uvicorn mcp_server:app --reload
