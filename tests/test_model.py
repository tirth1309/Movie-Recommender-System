import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import unittest
from unittest.mock import patch, MagicMock
from surprise import Dataset, Reader
import pandas as pd
from model_build.model import prepare_data_for_recommendation_model, build_model
from surprise.prediction_algorithms.matrix_factorization import SVD


class TestRecommendationFunctions(unittest.TestCase):

    def setUp(self):
        self.rating_range = (1, 5)

        self.train_df = pd.DataFrame({
            'user': [1, 1, 2, 2, 3],
            'item': [101, 102, 101, 103, 102],
            'rating': [4, 5, 3, 4, 5]
        })
        self.val_df = pd.DataFrame({
            'user': [4, 4, 5],
            'item': [103, 104, 104],
            'rating': [2, 3, 4]
        })

    def test_prepare_data_for_recommendation_model(self):
        train_data, valid_data = prepare_data_for_recommendation_model(self.train_df, self.val_df)

        # Assert train_data is an instance of surprise Dataset
        self.assertIsInstance(train_data, Dataset)

        # Assert valid_data is an instance of surprise Dataset
        self.assertIsInstance(valid_data, Dataset)

    def test_build_model(self):
        model_name = 'SVD'
        model = build_model(model_name)
        self.assertIsInstance(model, SVD)

    def test_build_model_with_invalid_model_name(self):
        with self.assertRaises(Exception) as context:
            build_model('InvalidModelName')
        self.assertTrue("Unrecognized model name passed" in str(context.exception))

if __name__ == '__main__':
    unittest.main()