import os


class Config:
    STRAVA_API_URL = "https://www.strava.com/api/v3"
    EFFORT_COLL_NAME = "effort_stats"
    SEGMENTS_COLL_NAME = "segments"
    AREAS_COLL_NAME = "areas"
    DATE_FORMAT = "%d-%m-%Y"

    def __init__(self):
        self.STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
        self.STRAVA_ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
        self.STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
        self.STRAVA_REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
        self.DB_URI = os.getenv("DB_URI")
        self.DB_NAME = os.getenv("DB_NAME")


class ConfigForTest(Config):
    def __init__(self):
        super().__init__()
        self.DB_NAME = os.getenv("TEST_DB_NAME")
