from db.database import Database
from models.TrailArea import TrailArea
from utils.config import Config


class AreasRepository:
    def __init__(self, db: Database, config: Config):
        self.config = config
        self.db = db

    def get_trail_areas(self):
        """Get all trail areas from the database."""
        areas = self.db.find_many(self.config.AREAS_COLL_NAME, {})
        validated_areas = [TrailArea(**area) for area in areas]
        return validated_areas
