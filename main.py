import sys
from datetime import datetime
from dotenv import load_dotenv
from db.database import Database, DatabaseConnectionError
from models.EnhancedSegment import EnhancedSegment
from models.RawSegment import RawSegment
from services.segments_repository import SegmentsRepository
from utils.logger import Logger
from utils.config import Config
from services.strava_api import StravaAPI, StravaApiRateLimitExceededError
from segments_data.segment_ids import segment_ids


def main():
    """Main function to fetch and write segment stats."""
    Logger.info("Starting script to update segments and effort data...")
    load_dotenv()
    try:
        config = Config()
        db = Database(config)
        strava_api = StravaAPI(config)
        segments_repository = SegmentsRepository(db, config)

        Logger.debug("Starting script to fetch and update segment stats...")
        for location, segments in segment_ids.items():
            for segment_id in segments.keys():
                segment_data = strava_api.get_segment(segment_id)
                raw_segment = RawSegment(**segment_data)
                timestamp = datetime.now().timestamp()
                enhanced_segment = EnhancedSegment.from_raw_segment(raw_segment, location, timestamp)
                segments_repository.write_segment_data(enhanced_segment)
    except DatabaseConnectionError as e:
        Logger.error(f"Error fetching segment stats: {e}")
        sys.exit(1)
    except StravaApiRateLimitExceededError as e:
        Logger.error(e)
        sys.exit(1)
    except Exception as e:
        Logger.error(f"Error: {e}")
        sys.exit(1)
    Logger.info("Script execution completed!")
    db.close_connection()
    sys.exit(0)


if __name__ == "__main__":
    main()
