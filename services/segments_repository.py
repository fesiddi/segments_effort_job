from db.database import Database
from models.EnhancedSegment import EnhancedSegment
from models.effort_data_class import EffortDataClass
from datetime import datetime
from utils.logger import Logger
from utils.config import Config


def map_segment_effort_data(enhanced_segment: EnhancedSegment) -> EffortDataClass:
    segment_id = enhanced_segment.id
    segment_name = enhanced_segment.name
    effort_count = enhanced_segment.effort_count
    fetch_date = datetime.now().strftime(Config.DATE_FORMAT)
    return EffortDataClass(segment_id, segment_name, effort_count, fetch_date)


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

    def update_effort_data(self, segment: EnhancedSegment):
        """Updates effort stats for a segment to the database."""
        segment_effort_data = map_segment_effort_data(segment)
        fetch_date = segment_effort_data.fetch_date
        # Check if an effort with the same fetch_date already exists
        existing_effort = self.db.find_one(
            self.config.EFFORT_COLL_NAME,
            {"segment_id": segment_effort_data.segment_id, "efforts.fetch_date": fetch_date}
        )

        if existing_effort:
            Logger.debug(f"Effort data for segment {segment_effort_data.segment_id} already exists in DB")
            Logger.debug(f"Existing effort: {existing_effort}")
            Logger.debug(f"SegmentEffortData: {segment_effort_data}")
            # If it does, update the effort_count of the existing effort
            self._update_one(
                self.config.EFFORT_COLL_NAME,
                {"segment_id": segment_effort_data.segment_id, "efforts.fetch_date": fetch_date},
                {"$set": {"efforts.$.effort_count": segment_effort_data.effort_count}},
            )
        else:
            Logger.debug(f"Effort data for segment {segment_effort_data.segment_id} does not exist in DB")
            Logger.debug(f"SegmentEffortData: {segment_effort_data}")
            # If it doesn't, add a new effort
            self._update_one(
                self.config.EFFORT_COLL_NAME,
                {"segment_id": segment_effort_data.segment_id},
                {
                    "$push": {
                        "efforts": {
                            "effort_count": segment_effort_data.effort_count,
                            "fetch_date": fetch_date,
                        }
                    }
                },
                upsert=False,
            )
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
