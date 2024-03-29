import os


class Config:
    STRAVA_API_URL = "https://www.strava.com/api/v3"
    STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
    STRAVA_ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
    STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
    STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
    DB_URI = os.getenv("DB_URI")
    DB_NAME = os.getenv("DB_NAME")
