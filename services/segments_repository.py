from db.database import Database
from models.effort_data_class import EffortDataClass
from datetime import datetime
from utils.logger import Logger


def map_segment_effort_data(full_segment):
    segment_id = full_segment.get("id")
    segment_name = full_segment.get("name")
    effort_count = full_segment.get("effort_count")
    fetch_date = datetime.now().strftime("%d-%m-%Y")
    return EffortDataClass(segment_id, segment_name, effort_count, fetch_date)


class SegmentsRepository:
    def __init__(self, db: Database):
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

    def update_effort_data(self, full_segment):
        """Updates effort stats for a segment to the database."""
        segment_effort_data = map_segment_effort_data(full_segment)
        fetch_date = segment_effort_data.fetch_date
        Logger.debug(f"Writing data for segment {segment_effort_data.id} to MongoDB")

        # Check if an effort with the same fetch_date already exists
        existing_effort = self.db.find_one(
            "segment_stats",
            {"segment_id": segment_effort_data.id, "efforts.fetch_date": fetch_date}
        )

        if existing_effort:
            # If it does, update the effort_count of the existing effort
            self._update_one(
                "segment_stats",
                {"segment_id": segment_effort_data.id, "efforts.fetch_date": fetch_date},
                {"$set": {"efforts.$.effort_count": segment_effort_data.effort_count}},
            )
        else:
            # If it doesn't, add a new effort
            self._update_one(
                "segment_stats",
                {"segment_id": segment_effort_data.id, "name": segment_effort_data.name},
                {
                    "$push": {
                        "efforts": {
                            "effort_count": segment_effort_data.effort_count,
                            "fetch_date": fetch_date,
                        }
                    }
                },
                upsert=True,
            )

        Logger.debug(f"Effort data for segment {segment_effort_data.id} written into DB")

    def update_full_segment_data(self, full_segment):
        """Write full data for a segment to the database."""
        segment_id = full_segment["id"]
        Logger.debug(f"Writing full data for segment {segment_id} to MongoDB")
        existing_document = self.db.find_one("segments", {"id": segment_id})
        if existing_document:
            self._update_one("segments", {"_id": existing_document.get("_id")}, {"$set": full_segment})
            Logger.debug(f"Data for segment {segment_id} updated into DB")
        else:
            self._insert_one("segments", full_segment)
            Logger.debug(f"Data for segment {segment_id} written into DB")

    def write_segment_data(self, segment_data):
        Logger.debug("Starting script to save segment data...")
        self.update_effort_data(segment_data)
        self.update_full_segment_data(segment_data)
