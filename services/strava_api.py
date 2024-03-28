import requests
import os
from utils.logger import Logger
from typing import Any, Dict


class StravaAPI:
    def __init__(self):
        self.strava_access_token = os.environ["STRAVA_ACCESS_TOKEN"]
        self.headers = {"Authorization": f"Bearer {self.strava_access_token}"}

    def get_segment(self, segment_id: str) -> Dict[str, Any]:
        segment = self._make_request(f"https://www.strava.com/api/v3/segments/{segment_id}")
        cleaned_segment = self.clean_segment(segment)
        return cleaned_segment

    def clean_segment(self, segment):
        return {
            "name": segment.get("name"),
            "id": segment.get("id"),
            "effort_count": segment.get("effort_count"),
        }

    def _make_request(self, url: str) -> Dict[str, Any]:
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
        auth_request = requests.post(
            f"https://www.strava.com/api/v3/oauth/token",
            data={
                "client_id": os.environ["STRAVA_CLIENT_ID"],
                "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
                "grant_type": "refresh_token",
                "refresh_token": os.environ["STRAVA_REFRESH_TOKEN"],
            },
        )
        if auth_request.status_code != 200:
            Logger.error("Error refreshing strava access token.")
            Logger.error(auth_request.json())
            raise Exception("Error refreshing strava access token.")
        self.strava_access_token = auth_request.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.strava_access_token}"}
