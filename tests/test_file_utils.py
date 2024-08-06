import unittest
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from unittest.mock import patch, mock_open

from utils.file_utils import read_movie_file
from utils.file_utils import load_properties


class TestReadMovieFile(unittest.TestCase):

    def setUp(self):
        # Create a temporary test file with sample data
        self.test_file_path = 'test_movies.txt'
        with open(self.test_file_path, 'w') as f:
            f.write("User1,Movie1,Movie2,Movie3\n")
            f.write("User2,Movie2,Movie4\n")
            f.write("User3,Movie3\n")

    def tearDown(self):
        # Remove the temporary test file after each test case
        os.remove(self.test_file_path)

    def test_read_movie_file(self):
        expected_output = {
            'User1': {'Movie1', 'Movie2', 'Movie3'},
            'User2': {'Movie2', 'Movie4'},
            'User3': {'Movie3'}
        }
        self.assertEqual(read_movie_file(self.test_file_path), expected_output)



if __name__ == '__main__':
    unittest.main()