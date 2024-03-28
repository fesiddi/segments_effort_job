from database import Database
from segment_effort_data import SegmentEffortData


class SegmentStatsDAO:
    def __init__(self, db: Database):
        self.db = db

    def update_segment_effort_data(self, segment: SegmentEffortData):
        self.db.update_segment_effort_data(segment)
