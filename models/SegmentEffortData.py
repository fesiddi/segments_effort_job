from typing import List
from pydantic import BaseModel


class Effort(BaseModel):
    effort_count: int
    fetch_date: str


class SegmentEffortData(BaseModel):
    segment_id: int
    name: str
    efforts: List[Effort]
