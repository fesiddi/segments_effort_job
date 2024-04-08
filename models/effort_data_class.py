from dataclasses import dataclass


@dataclass
class EffortDataClass:
    segment_id: int
    name: str
    effort_count: int
    fetch_date: str
