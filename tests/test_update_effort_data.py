from datetime import datetime

import pytest
from unittest.mock import patch
from db.database import Database
from models.RawSegment import Map
from utils.config import Config
from models.EnhancedSegment import EnhancedSegment
from dotenv import load_dotenv
from services.segments_repository import SegmentsRepository

load_dotenv()


@pytest.fixture
def segment():
    return EnhancedSegment(
        id=1,
        name="Test Segment",
        alt_name="Test Alt Name",
        trail_area="Test Trail Area",
        average_grade=0.0,
        distance=0.0,
        start_lat=0.0,
        start_lng=0.0,
        end_lat=0.0,
        end_lng=0.0,
        local_legend=None,
        star_count=0,
        effort_count=0,
        athlete_count=0,
        kom="Test KOM",
        map=Map(id='1', polyline='Test Polyline', resource_state=1),
        polyline="Test Polyline",
        timestamp=datetime.now().timestamp()
    )


@pytest.fixture
def segments_repository():
    config = Config()
    db = Database(config)
    return SegmentsRepository(db, config)


def test_update_segment_data_when_segment_exists(segment, segments_repository):
    with patch.object(Database, 'find_one') as mock_find_one, patch.object(SegmentsRepository, '_update_one') as mock_update_one, patch.object(SegmentsRepository, '_insert_one') as mock_insert_one:
        mock_find_one.return_value = {"_id": "test_id"}
        segments_repository.update_segment_data(segment)
        mock_update_one.assert_called_once_with(
            "segments",
            {"_id": "test_id"},
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
                    "local_legend": None,
                    "star_count": segment.star_count,
                    "effort_count": segment.effort_count,
                    "athlete_count": segment.athlete_count,
                    "kom": segment.kom,
                    "map": segment.map.to_dict(),
                    "polyline": segment.polyline,
                    "timestamp": segment.timestamp,
                }
            }
        )
        mock_insert_one.assert_not_called()


def test_update_segment_data_when_segment_does_not_exist(segment, segments_repository):
    with patch.object(Database, 'find_one') as mock_find_one, patch.object(SegmentsRepository, '_update_one') as mock_update_one, patch.object(SegmentsRepository, '_insert_one') as mock_insert_one:
        mock_find_one.return_value = None
        segments_repository.update_segment_data(segment)
        mock_insert_one.assert_called_once_with(
            "segments",
            {
                "id": segment.id,
                "name": segment.name,
                "alt_name": segment.alt_name,
                "trail_area": segment.trail_area,
                "average_grade": segment.average_grade,
                "distance": segment.distance,
                "difficulty": segment.difficulty,
                "popularity": segment.popularity,
                "start_lat": segment.start_lat,
                "start_lng": segment.start_lng,
                "end_lat": segment.end_lat,
                "end_lng": segment.end_lng,
                "local_legend": None,
                "star_count": segment.star_count,
                "effort_count": segment.effort_count,
                "athlete_count": segment.athlete_count,
                "kom": segment.kom,
                "map": segment.map.to_dict(),
                "polyline": segment.polyline,
                "timestamp": segment.timestamp,
            }
        )
        mock_update_one.assert_not_called()


def test_update_effort_data_when_effort_exists(segment, segments_repository):
    fetch_date = datetime.now().strftime("%d-%m-%Y")
    with patch.object(Database, 'find_one') as mock_find_one, patch.object(SegmentsRepository, '_update_one') as mock_update_one:
        mock_find_one.return_value = True
        segments_repository.update_effort_data(segment)
        mock_update_one.assert_called_once_with(
            segments_repository.config.EFFORT_COLL_NAME,
            {"segment_id": segment.id, "efforts.fetch_date": fetch_date},
            {"$set": {"efforts.$.effort_count": segment.effort_count}},
        )


def test_update_effort_data_when_effort_does_not_exist(segment, segments_repository):
    with patch.object(Database, 'find_one') as mock_find_one, patch.object(SegmentsRepository, '_update_one') as mock_update_one:
        mock_find_one.return_value = None
        segments_repository.update_effort_data(segment)
        mock_update_one.assert_called_once_with(
            segments_repository.config.EFFORT_COLL_NAME,
            {"segment_id": segment.id},
            {"$push": {"efforts": {"fetch_date": datetime.now().strftime("%d-%m-%Y"), "effort_count": segment.effort_count}}},
            upsert=False
        )