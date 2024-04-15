from unittest.mock import patch
from services.strava_api import StravaAPI, StravaApiError
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


def test_get_segment_effort_data_rate_limit_exceeded():
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    segment_id = "12345"
    with patch.object(StravaAPI, '_handle_request') as mock_handle_request:
        mock_handle_request.side_effect = Exception("Strava API Rate limit exceeded")
        try:
            strava_api.get_segment(segment_id)
        except Exception as e:
            assert str(e) == "Strava API Rate limit exceeded"
        mock_handle_request.assert_called_once_with(f"{config.STRAVA_API_URL}/segments/{segment_id}")


def test_get_segment_effort_data_error():
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    segment_id = "12345"
    with patch.object(StravaAPI, '_handle_request') as mock_handle_request:
        mock_handle_request.side_effect = Exception("Error fetching data from strava API.")
        try:
            strava_api.get_segment(segment_id)
        except Exception as e:
            assert str(e) == "Error fetching data from strava API."
        mock_handle_request.assert_called_once_with(f"{config.STRAVA_API_URL}/segments/{segment_id}")


def test_refresh_token():
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"refresh_token": "2ac7c34309b1e648d04e4c7c44e6e5f7e67c4ccd", "access_token": "new_access_token"}
        strava_api._refresh_token()
        assert config.STRAVA_REFRESH_TOKEN == "2ac7c34309b1e648d04e4c7c44e6e5f7e67c4ccd"
        assert config.STRAVA_ACCESS_TOKEN == "new_access_token"
        mock_post.assert_called_once_with(
            f"https://www.strava.com/api/v3/oauth/token",
            data={
                "client_id": config.STRAVA_CLIENT_ID,
                "client_secret": config.STRAVA_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": "2ac7c34309b1e648d04e4c7c44e6e5f7e67c4ccd",
            },
        )


def test_refresh_token_error():
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"error": "invalid_grant"}
        try:
            strava_api._refresh_token()
        except Exception as e:
            assert str(e) == "Error refreshing strava access token."
        mock_post.assert_called_once_with(
            f"https://www.strava.com/api/v3/oauth/token",
            data={
                "client_id": config.STRAVA_CLIENT_ID,
                "client_secret": config.STRAVA_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": config.STRAVA_REFRESH_TOKEN,
            },
        )


def test_handle_request():
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": 12345, "name": "Test Segment", "effort_count": 10}
        segment_data = strava_api._handle_request(f"{config.STRAVA_API_URL}/segments/12345")
        assert segment_data["id"] == 12345
        assert segment_data["name"] == "Test Segment"
        assert segment_data["effort_count"] == 10
        mock_get.assert_called_once_with(f"{config.STRAVA_API_URL}/segments/12345", headers={"Authorization": f"Bearer {config.STRAVA_REFRESH_TOKEN}"})


def test_handle_request_rate_limit_exceeded():
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 429
        try:
            strava_api._handle_request(f"{config.STRAVA_API_URL}/segments/12345")
        except Exception as e:
            assert str(e) == "Strava API Rate limit exceeded"
        mock_get.assert_called_once_with(f"{config.STRAVA_API_URL}/segments/12345", headers={"Authorization": f"Bearer {config.STRAVA_REFRESH_TOKEN}"})


def test_handle_request_error():
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 400
        mock_get.return_value.json.return_value = {"error": "Bad Request"}
        try:
            strava_api._handle_request(f"{config.STRAVA_API_URL}/segments/12345")
        except Exception as e:
            assert str(e) == "Error fetching data from strava API."
        mock_get.assert_called_once_with(f"{config.STRAVA_API_URL}/segments/12345", headers={"Authorization": f"Bearer {config.STRAVA_REFRESH_TOKEN}"})


def test_handle_request_refresh_token():
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    with patch('requests.get') as mock_get, patch.object(StravaAPI, '_refresh_token') as mock_refresh_token:
        mock_get.return_value.status_code = 500
        try:
            strava_api._handle_request(f"{config.STRAVA_API_URL}/segments/12345")
        except StravaApiError as e:
            assert str(e) == "Error fetching data from strava API."
        mock_refresh_token.assert_not_called()


def test_handle_request_refresh_token_error():
    config = ConfigForTest()
    strava_api = StravaAPI(config)
    with patch('requests.get') as mock_get, patch.object(StravaAPI, '_refresh_token') as mock_refresh_token:
        mock_get.return_value.status_code = 401
        mock_refresh_token.side_effect = Exception("Error refreshing strava access token.")
        try:
            strava_api._handle_request(f"{config.STRAVA_API_URL}/segments/12345")
        except Exception as e:
            assert str(e) == "Error refreshing strava access token."
        mock_refresh_token.assert_called_once()

