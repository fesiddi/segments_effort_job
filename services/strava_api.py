import requests
import os
from utils.logger import Logger
from typing import Any, Dict
from utils.config import Config


class StravaAPI:
    def __init__(self, config: Config):
        self.config = config
        self.headers = {"Authorization": f"Bearer {self.config.STRAVA_REFRESH_TOKEN}"}

    def get_segment(self, segment_id: str) -> Dict[str, Any]:
        segment = self._make_request(f"{self.config.STRAVA_API_URL}/segments/{segment_id}")
        return segment

    def _make_request(self, url: str) -> Dict[str, Any]:
        Logger.info(f"Fetching Strava for segment: {url.split('/')[-1]}")
        response = requests.get(url, headers=self.headers)
        if response.status_code == 401:
            self._refresh_token()
            response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            Logger.error("Error fetching data from strava API.")
            Logger.error(response.json())
            raise Exception("Error fetching data from strava API.")
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
            raise Exception("Error refreshing strava access token.")
        self.config.STRAVA_REFRESH_TOKEN = auth_request.json().get("refresh_token")
        self.config.STRAVA_ACCESS_TOKEN = auth_request.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.config.STRAVA_ACCESS_TOKEN}"}

