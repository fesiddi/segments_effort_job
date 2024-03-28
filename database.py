import os
from datetime import datetime

from pymongo.errors import ConfigurationError
from pymongo.mongo_client import MongoClient

from logger import Logger
from segment_effort_data import SegmentEffortData


class DatabaseConnectionError(Exception):
    """Exception raised for errors in the database connection.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Database connection error"):
        self.message = message
        super().__init__(self.message)


class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.db_uri = os.environ["DB_URI"]
        self.db_name = os.environ["DB_NAME"]

        if not self.db_uri or not self.db_name:
            Logger.error("DB_URI and DB_NAME environment variables must be set")
            raise DatabaseConnectionError("DB_URI and DB_NAME environment variables must be set")
        try:
            self.client = MongoClient(self.db_uri)
            self.db = self.client[self.db_name]
            Logger.debug("Connected to MongoDB")
        except ConfigurationError:
            Logger.error(
                "An Invalid URI host error was received. Is your Atlas host name correct in your connection string?"
            )
            raise DatabaseConnectionError(
                "An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
        except Exception as e:
            Logger.error(f"An error occurred: {e}")
            raise DatabaseConnectionError(f"An error occurred: {e}")

    def update_segment_effort_data(self, segment: SegmentEffortData):
        fetch_date = datetime.now().strftime("%d-%m-%Y")
        Logger.debug(f"Writing data for segment {segment.id} to MongoDB")

        # Check if an effort with the same fetch_date already exists
        existing_effort = self.db.segment_stats.find_one(
            {"segment_id": segment.id, "efforts.fetch_date": fetch_date}
        )

        if existing_effort:
            # If it does, update the effort_count of the existing effort
            self.db.segment_stats.update_one(
                {"segment_id": segment.id, "efforts.fetch_date": fetch_date},
                {"$set": {"efforts.$.effort_count": segment.effort_count}},
            )
        else:
            # If it doesn't, add a new effort
            self.db.segment_stats.update_one(
                {"segment_id": segment.id, "name": segment.name},
                {
                    "$push": {
                        "efforts": {
                            "effort_count": segment.effort_count,
                            "fetch_date": fetch_date,
                        }
                    }
                },
                upsert=True,
            )

        Logger.debug("Data written to MongoDB")

    def get_segment_effort_data(self, segment_id):
        Logger.debug(f"Fetching data for segment {segment_id} from MongoDB")
        segment_effort_data = self.db.segment_stats.find_one({"segment_id": segment_id})
        if not segment_effort_data:
            Logger.info(f"No data found for segment {segment_id}")
            return None
        return segment_effort_data

    def close_connection(self):
        self.client.close()
        Logger.debug("Connection to MongoDB closed")
