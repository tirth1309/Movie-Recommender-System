import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import unittest
from unittest import mock
from surprise import Dataset, Reader

from surprise.prediction_algorithms.matrix_factorization import SVD

import joblib
from unittest.mock import MagicMock, patch
from model_build.train import evaluate, train, predict


class TestEvaluateFunction(unittest.TestCase):

    @patch('model_build.train.accuracy')
    def test_evaluate(self, mock_accuracy):
        model = MagicMock()
        valid_data = MagicMock()
        # Mocking raw_ratings and test return value
        valid_data.raw_ratings = [(1, 1, 3, None), (2, 2, 4, None)]  # Example raw ratings
        mock_accuracy.rmse.return_value = 1.5  # Mocking RMSE value

        # Call the function
        rmse = evaluate(model, valid_data)

        # Assert the returned RMSE value
        self.assertEqual(rmse, 1.5)  # Ensure the returned RMSE matches the mocked value


    def test_train(self):
        training_args = {
            'model_name': 'SVD',
            'file_path': 'user_data_test.csv',
        }
        trained_model, train_data, valid_data, train_df, val_df = train(training_args)
        self.assertIsInstance(trained_model, SVD)
        self.assertIsInstance(train_data, Dataset)
        self.assertEqual(len(train_df), 5)

    def test_predict(self):

        trained_model = MagicMock()
        all_movies_list = ['Movie1', 'Movie2', 'Movie3']
        user_movie_list = []

        recommendations, time = predict(trained_model, '202605', all_movies_list, user_movie_list, 20, False)
        print(recommendations)


if __name__ == '__main__':
    unittest.main()