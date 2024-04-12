import unittest
from unittest.mock import patch
from services.areas_repository import AreasRepository
from utils.config import ConfigForTest


class TestAreasRepository(unittest.TestCase):
    @patch('db.database.Database')
    def test_get_trail_areas(self, mock_db):
        # Arrange
        config = ConfigForTest()
        mock_db_instance = mock_db.return_value
        mock_db_instance.find_many.return_value = [{
            'name': 'Test Area',
            's_name': 'Test short name',
            'description': 'Test description',
            'local_riders': [{'name': 'Test Rider', 'strava_id': '123'}],
            'instagram': ['Test Instagram'],
            'trail_bases': [{'name': 'Test Base', 'coordinates': (12.34, 56.78)}]  # Provide coordinates as a tuple
        }]
        areas_repository = AreasRepository(mock_db_instance, config)

        # Act
        result = areas_repository.get_trail_areas()

        # Assert
        mock_db_instance.find_many.assert_called_once_with(config.AREAS_COLL_NAME, {})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'Test Area')
        self.assertEqual(result[0].s_name, 'Test short name')
        self.assertEqual(result[0].description, 'Test description')
        self.assertEqual(result[0].local_riders[0].name, 'Test Rider')
        self.assertEqual(result[0].local_riders[0].strava_id, '123')
        self.assertEqual(result[0].instagram[0], 'Test Instagram')
        self.assertEqual(result[0].trail_bases[0].name, 'Test Base')
        self.assertEqual(result[0].trail_bases[0].coordinates, (12.34, 56.78))  # Expect coordinates as a tuple
