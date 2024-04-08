from typing import List, Optional
from pydantic import BaseModel


class LocalRider(BaseModel):
    name: str
    strava_id: str


class TrailBase(BaseModel):
    coordinates: List[List[float]]
    name: Optional[str]


class TrailArea(BaseModel):
    name: str
    s_name: str
    description: str
    local_riders: List[LocalRider]
    instagram: List[str]
    trail_bases: Optional[List[TrailBase]]
