from db.database import Database
from models.EnhancedSegment import EnhancedSegment
from models.SegmentEffortData import Effort, SegmentEffortData
from datetime import datetime
from utils.logger import Logger
from utils.config import Config


def map_segment_effort_data(enhanced_segment: EnhancedSegment) -> SegmentEffortData:
    segment_id = enhanced_segment.id
    segment_name = enhanced_segment.name
    effort_count = enhanced_segment.effort_count
    fetch_date = datetime.now().strftime(Config.DATE_FORMAT)
    effort = Effort(effort_count=effort_count, fetch_date=fetch_date)
    return SegmentEffortData(segment_id=segment_id, name=segment_name, efforts=[effort])


class SegmentsRepository:
    def __init__(self, db: Database, config: Config):
        self.config = config
        self.db = db

    def _update_one(self, collection_name, query, new_values, upsert=False):
        """Update a single document in the database."""
        try:
            self.db.update_one(collection_name, query, new_values, upsert=upsert)
        except Exception as e:
            Logger.error(f"An error occurred while updating the database: {e}")
            raise

    def _insert_one(self, collection_name, document):
        """Insert a single document into the database."""
        try:
            self.db.insert_one(collection_name, document)
        except Exception as e:
            Logger.error(f"An error occurred while inserting into the database: {e}")
            raise

    def update_existing_effort(self, segment_effort_data, fetch_date):
        """Update the effort_count of an existing effort."""
        self._update_one(
            self.config.EFFORT_COLL_NAME,
            {"segment_id": segment_effort_data.segment_id, "efforts.fetch_date": fetch_date},
            {"$set": {"efforts.$.effort_count": segment_effort_data.efforts[0].effort_count}},
        )

    def add_new_effort(self, segment_effort_data, fetch_date):
        """Add a new entry for the efforts array."""
        self._update_one(
            self.config.EFFORT_COLL_NAME,
            {"segment_id": segment_effort_data.segment_id},
            {
                "$push": {
                    "efforts": {
                        "effort_count": segment_effort_data.efforts[0].effort_count,
                        "fetch_date": fetch_date,
                    }
                }
            },
            upsert=False,
        )

    def create_new_effort_data(self, segment_effort_data):
        """Create a new effort data for the segment."""
        self._insert_one(
            self.config.EFFORT_COLL_NAME,
            {"segment_id": segment_effort_data.segment_id, "name": segment_effort_data.name,
             "efforts": [{"effort_count": segment_effort_data.efforts[0].effort_count,
                          "fetch_date": segment_effort_data.efforts[0].fetch_date}]},
        )

    def update_effort_data(self, segment: EnhancedSegment):
        """Updates effort stats for a segment to the database."""
        segment_effort_data = map_segment_effort_data(segment)
        fetch_date = segment_effort_data.efforts[0].fetch_date
        # Check if an effort with the same fetch_date already exists
        existing_effort_data = self.db.find_one(
            self.config.EFFORT_COLL_NAME,
            {"segment_id": segment_effort_data.segment_id}
        )

        if existing_effort_data:
            Logger.debug(f"Effort data for segment {segment_effort_data.segment_id} already exists in DB")
            Logger.debug(f"Existing effort: {existing_effort_data}")
            Logger.debug(f"SegmentEffortData: {segment_effort_data}")
            # If it does, check if there is an effort with the same fetch_date
            existing_effort_same_date = next(
                (effort for effort in existing_effort_data['efforts'] if effort['fetch_date'] == fetch_date), None)
            if existing_effort_same_date:
                # If it's the same, update the effort_count of the existing effort
                self.update_existing_effort(segment_effort_data, fetch_date)
            else:
                # If the fetch date is not the same, add a new entry for the efforts array
                self.add_new_effort(segment_effort_data, fetch_date)
        else:
            # If it doesn't, create a new effort data for the segment
            self.create_new_effort_data(segment_effort_data)
        Logger.debug(f"Effort data for segment {segment_effort_data.segment_id} written into DB")

    def update_segment_data(self, segment: EnhancedSegment):
        """Updates data for a segment to the database."""
        segment_id = segment.id
        local_legend_dict = segment.local_legend.to_dict() if segment.local_legend else None
        segment_map_dict = segment.map.to_dict()
        existing_document = self.db.find_one("segments", {"id": segment_id})
        if existing_document:
            self._update_one(
                "segments",
                {"_id": existing_document.get("_id")},
                {
                    "$set":
                    {
                        "name": segment.name,
                        "average_grade": segment.average_grade,
                        "distance": segment.distance,
                        "start_lat": segment.start_lat,
                        "start_lng": segment.start_lng,
                        "end_lat": segment.end_lat,
                        "end_lng": segment.end_lng,
                        "local_legend": local_legend_dict,
                        "star_count": segment.star_count,
                        "effort_count": segment.effort_count,
                        "athlete_count": segment.athlete_count,
                        "kom": segment.kom,
                        "map": segment_map_dict,
                        "polyline": segment.polyline,
                        "timestamp": segment.timestamp,
                    }
                }
            )
            Logger.debug(f"Data for segment {segment_id} updated into DB")
        else:
            self._insert_one("segments", segment.to_dict())
            Logger.debug(f"Data for segment {segment_id} written into DB")

    def write_segment_data(self, segment_data: EnhancedSegment):
        """Write segment data and effort data to the database."""
        self.update_effort_data(segment_data)
        self.update_segment_data(segment_data)
