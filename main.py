import sys

from database import Database, DatabaseConnectionError
from segment_stats_dao import SegmentStatsDAO
from logger import Logger
from segment_ids import segment_ids_dict
from segment_effort_data_fetcher import fetch_segment_effort_stats


def main():
    """Main function to fetch and write segment stats."""
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

    db.close_connection()
    Logger.info("Segments effort stats update completed!")
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
