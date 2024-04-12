from unittest.mock import patch
from services.strava_api import StravaAPI
from dotenv import load_dotenv
from utils.config import ConfigForTest

load_dotenv()


@patch.object(StravaAPI, 'get_segment')
def test_get_segment_effort_data(mock_get_segment):
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    segment_id = "12345"
    mock_get_segment.return_value = {"id": segment_id, "name": "Test Segment", "effort_count": 10}
    segment_effort_data = strava_api.get_segment(segment_id)
    assert segment_effort_data["id"] == segment_id
    assert segment_effort_data["name"] == "Test Segment"
    assert segment_effort_data["effort_count"] == 10
    mock_get_segment.assert_called_once_with(segment_id)


def test_get_real_segment_effort_data():
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    segment_id = "11451094"
    segment_effort_data = strava_api.get_segment(segment_id)
    assert segment_effort_data is not None
    assert segment_effort_data["id"] == int(segment_id)
    assert segment_effort_data["name"] == "Catorcio"
