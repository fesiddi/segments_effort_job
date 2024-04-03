from pydantic import BaseModel
from typing import Optional
from models.RawSegment import RawSegment, Map, LocalLegend


class EnhancedSegment(BaseModel):
    id: int
    name: str
    alt_name: str
    trail_area: str
    average_grade: float
    distance: float
    difficulty: Optional[str] = ''
    popularity: Optional[int] = 0
    start_lat: Optional[float]
    start_lng: Optional[float]
    end_lat: Optional[float]
    end_lng: Optional[float]
    local_legend: Optional[LocalLegend]
    star_count: int
    effort_count: int
    athlete_count: int
    kom: Optional[str]
    map: Map
    polyline: Optional[str]
    timestamp: float

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'alt_name': self.alt_name,
            'trail_area': self.trail_area,
            'average_grade': self.average_grade,
            'distance': self.distance,
            'difficulty': self.difficulty,
            'popularity': self.popularity,
            'start_lat': self.start_lat,
            'start_lng': self.start_lng,
            'end_lat': self.end_lat,
            'end_lng': self.end_lng,
            'local_legend': self.local_legend.to_dict() if self.local_legend else None,
            'star_count': self.star_count,
            'effort_count': self.effort_count,
            'athlete_count': self.athlete_count,
            'kom': self.kom,
            'map': self.map.to_dict(),
            'polyline': self.polyline,
            'timestamp': self.timestamp,
        }

    @classmethod
    def from_raw_segment(cls, segment: RawSegment, trail_area: str, timestamp: float):
        return cls(
            name=segment.name,
            alt_name=segment.name,
            id=segment.id,
            trail_area=trail_area,
            average_grade=segment.average_grade,
            distance=segment.distance,
            difficulty=cls.model_fields['difficulty'].default,
            popularity=cls.model_fields['popularity'].default,
            start_lat=segment.start_latlng.lat,
            start_lng=segment.start_latlng.lng,
            end_lat=segment.end_latlng.lat,
            end_lng=segment.end_latlng.lng,
            local_legend=segment.local_legend,
            star_count=segment.star_count,
            effort_count=segment.effort_count,
            athlete_count=segment.athlete_count,
            kom=segment.xoms.kom,
            map=segment.map,
            polyline=segment.map.polyline,
            timestamp=timestamp,
        )
