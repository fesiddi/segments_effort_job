from dataclasses import dataclass


@dataclass
class EffortDataClass:
    id: str
    name: str
    effort_count: int
    fetch_date: str
