from datetime import datetime
from logger import Logger
from strava_api import StravaAPI
from segment_effort_data import SegmentEffortData


def fetch_segment_effort_stats(segment_id: str) -> SegmentEffortData:
    """Fetch effort stats for a segment and return a dictionary with the data."""
    Logger.debug(f"Fetching stats for segment {segment_id}...")
    strava_api = StravaAPI()
    segment_data = strava_api.get_segment(segment_id)

    segment_effort_data = SegmentEffortData(
        id=segment_data.get("id"),
        name=segment_data.get("name"),
        effort_count=segment_data.get("effort_count"),
        fetch_date=datetime.now().strftime("%d-%m-%Y"),
    )
    return segment_effort_data
