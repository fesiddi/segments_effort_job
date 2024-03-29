from db.database import Database
from models.segment_effort_data import SegmentEffortData
from datetime import datetime


class SegmentStatsDAO:
    def __init__(self, db: Database):
        self.db = db

    def update_segment_effort_data(self, segment_data: dict):
        """Update the effort data for a segment in the database."""
        segment_effort_data = SegmentEffortData(
            id=segment_data.get("id"),
            name=segment_data.get("name"),
            effort_count=segment_data.get("effort_count"),
            fetch_date=datetime.now().strftime("%d-%m-%Y"),
        )
        self.db.update_segment_effort_data(segment_effort_data)

    def update_full_segment_data(self, full_segment):
        self.db.save_or_update_full_segment_data(full_segment)
