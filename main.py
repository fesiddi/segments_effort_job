import sys
from dotenv import load_dotenv
from db.database import Database, DatabaseConnectionError
from services.segments_repository import SegmentsRepository
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
        segments_repository = SegmentsRepository(db)

        Logger.debug("Starting script to fetch and update segment stats...")
        for location, segments in segment_ids.items():
            for segment_id in segments.keys():
                segment_data = strava_api.get_segment(segment_id)
                segments_repository.write_segment_data(segment_data)
    except DatabaseConnectionError as e:
        Logger.error(f"Error fetching segment stats: {e}")
        sys.exit(1)
    Logger.info("Segments effort stats update completed!")
    db.close_connection()
    sys.exit(0)


if __name__ == "__main__":
    main()
