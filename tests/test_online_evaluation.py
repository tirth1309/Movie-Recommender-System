import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import unittest
from unittest.mock import patch, MagicMock
from evaluation.online_evaluation import get_online_evaluation_statistics
from jproperties import Properties

class TestOnlineEvaluationStatistics(unittest.TestCase):

    @patch('evaluation.online_evaluation.load_properties')
    @patch('evaluation.online_evaluation.read_movie_file')
    def test_get_online_evaluation_statistics(self, mock_read_movie_file, mock_load_properties):
        # Mocking configuration data
        mock_config = Properties()
        mock_config['MOVIES_WATCHED_FILE_PATH'] = 'mock_movies_watched_file_path'
        mock_config['MOVIES_RECOMMENDED_FILE_PATH'] = 'mock_movies_recommended_file_path'

        # mock_config = {
        #     'MOVIES_WATCHED_FILE_PATH': 'mock_movies_watched_file_path',
        #     'MOVIES_RECOMMENDED_FILE_PATH': 'mock_movies_recommended_file_path'
        # }
        mock_load_properties.return_value = MagicMock(get=lambda x: mock_config.get(x))

        # Mocking movie data
        mock_movies_watched_data = {
            'user1': ['movie1', 'movie2'],
            'user2': ['movie3', 'movie4']
        }
        mock_movies_recommended_data = {
            'user1': ['movie1', 'movie3'],
            'user2': ['movie2', 'movie4']
        }
        mock_read_movie_file.side_effect = lambda x: mock_movies_watched_data if x == 'mock_movies_watched_file_path' else mock_movies_recommended_data

        # Calling the function
        macro_precision, macro_recall, micro_precision, micro_recall, recommendation_adoption = get_online_evaluation_statistics()

        # Assertions
        #self.assertAlmostEqual(macro_precision, 0.5)  # Expected value based on mock data
        #self.assertAlmostEqual(macro_recall, 0.5)     # Expected value based on mock data
        #self.assertAlmostEqual(micro_precision, 0.5)  # Expected value based on mock data
        #self.assertAlmostEqual(micro_recall, 0.5)     # Expected value based on mock data
        #self.assertAlmostEqual(recommendation_adoption, 1) # Expected value based on mock data

if __name__ == '__main__':
    unittest.main()