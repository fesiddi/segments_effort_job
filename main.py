import sys
import time
from dotenv import load_dotenv


from db.database import Database, DatabaseConnectionError
from services.segment_stats_dao import SegmentStatsDAO
from utils.logger import Logger
from segments_data.segment_ids import test_segment_ids_dict as segment_ids_dict
from services.segment_effort_data_fetcher import fetch_segment_effort_stats


def main():
    """Main function to fetch and write segment stats."""
    Logger.info("Starting segment effort stats update...")
    load_dotenv()
    try:
        db = Database()
        dao = SegmentStatsDAO(db)
        fetch_and_write_segments_stats(dao)
    except DatabaseConnectionError as e:
        Logger.error(f"Error fetching segment stats: {e}")
        sys.exit(1)
    except Exception as e:
        Logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
    Logger.info("Segments effort stats update completed!")
    time.sleep(1)
    db.upload_logs_to_db()
    db.close_connection()
    sys.exit(0)


def fetch_and_write_segments_stats(dao: SegmentStatsDAO):
    """Fetch and write effort stats for all segments in the segment_ids_dict into the database."""
    Logger.debug("Fetching and writing segment stats...")
    for location, segments in segment_ids_dict.items():
        for segment_id in segments.keys():
            segment_stats = fetch_segment_effort_stats(segment_id)
            dao.update_segment_effort_data(segment_stats)


if __name__ == "__main__":
    main()
