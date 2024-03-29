import sys
import time
from dotenv import load_dotenv


from db.database import Database, DatabaseConnectionError
from services.segment_stats_dao import SegmentStatsDAO
from utils.logger import Logger
from utils.config import Config
from services.strava_api import StravaAPI
from segments_data.segment_ids import segment_ids


def main():
    """Main function to fetch and write segment stats."""
    Logger.info("Starting segment effort stats update...")
    load_dotenv()
    try:
        config = Config()
        db = Database(config)
        strava_api = StravaAPI(config)
        dao = SegmentStatsDAO(db)
        fetch_and_write_segments_stats(dao, strava_api)
    except DatabaseConnectionError as e:
        Logger.error(f"Error fetching segment stats: {e}")
        sys.exit(1)
    Logger.info("Segments effort stats update completed!")
    time.sleep(1)
    db.upload_logs_to_db()
    db.close_connection()
    sys.exit(0)


def fetch_and_write_segments_stats(dao: SegmentStatsDAO, strava_api: StravaAPI):
    """Fetch and write effort stats for all segments in the segment_ids_dict into the database."""
    Logger.debug("Starting script to fetch and update segment stats...")
    for location, segments in segment_ids.items():
        for segment_id in segments.keys():
            segment_data = strava_api.get_segment(segment_id)
            dao.update_segment_effort_data(segment_data)
            dao.update_full_segment_data(segment_data)


if __name__ == "__main__":
    main()
