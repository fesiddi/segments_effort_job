import requests
from utils.logger import Logger
from typing import Any, Dict
from utils.config import Config


class StravaApiRateLimitExceededError(Exception):
    pass


class StravaApiRefreshTokenError(Exception):
    pass


class StravaApiError(Exception):
    pass


class StravaAPI:
    def __init__(self, config: Config):
        self.config = config
        self.headers = {"Authorization": f"Bearer {self.config.STRAVA_REFRESH_TOKEN}"}

    def get_segment(self, segment_id: str) -> Dict[str, Any]:
        segment = self._handle_request(f"{self.config.STRAVA_API_URL}/segments/{segment_id}")
        return segment

    def _handle_request(self, url: str) -> Dict[str, Any]:
        Logger.debug(f"Fetching Strava for segment: {url.split('/')[-1]}")
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            self._refresh_token()
            response = requests.get(url, headers=self.headers)
        if response.status_code == 429:
            raise StravaApiRateLimitExceededError("Strava API Rate limit exceeded")
        if response.status_code != 200:
            Logger.error("Error fetching data from strava API.")
            Logger.error(response.status_code)
            Logger.error(response.json())
            raise StravaApiError("Error fetching data from strava API.")
        return response.json()

    def _refresh_token(self):
        Logger.info("Refreshing strava access token.")
        auth_request = requests.post(
            f"https://www.strava.com/api/v3/oauth/token",
            data={
                "client_id": self.config.STRAVA_CLIENT_ID,
                "client_secret": self.config.STRAVA_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": self.config.STRAVA_REFRESH_TOKEN,
            },
        )
        if auth_request.status_code != 200:
            Logger.error("Error refreshing strava access token.")
            Logger.error(auth_request.json())
            raise StravaApiRefreshTokenError("Error refreshing strava access token.")
        self.config.STRAVA_REFRESH_TOKEN = auth_request.json().get("refresh_token")
        self.config.STRAVA_ACCESS_TOKEN = auth_request.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.config.STRAVA_ACCESS_TOKEN}"}
