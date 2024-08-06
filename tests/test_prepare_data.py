import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import unittest
import pandas as pd
from model_build.prepare_data import prepare_data_from_csv  # Import your function

class TestPrepareDataFromCSV(unittest.TestCase):

    def setUp(self):
        # Create a sample CSV file for testing
        self.sample_data = {
            'User_ID': [1, 1, 1, 2, 2, 2, 3, 3, 3],
            'Movie_Ids': [101, 102, 103, 101, 102, 103, 101, 102, 103],
            'Movie_Rating': [4, 3, 5, 3, 5, 4, 5, 4, 3]
        }
        self.df = pd.DataFrame(self.sample_data)
        self.file_path = "test_data.csv"
        self.df.to_csv(self.file_path, index=False)

    def tearDown(self):
        # Remove the sample CSV file after testing
        import os
        os.remove(self.file_path)

    def test_prepare_data_from_csv(self):
        train_df, val_df = prepare_data_from_csv(self.file_path)

        # Check if train_df and val_df are pandas DataFrames
        self.assertIsInstance(train_df, pd.DataFrame)
        self.assertIsInstance(val_df, pd.DataFrame)

        # Check if train_df has the correct number of entries
        self.assertEqual(len(train_df), 6)

        # Check if val_df has the correct number of entries
        self.assertEqual(len(val_df), 3)

        # Check if train_df contains the correct columns
        self.assertListEqual(list(train_df.columns), ['user', 'item', 'rating'])

        # Check if val_df contains the correct columns
        self.assertListEqual(list(val_df.columns), ['user', 'item', 'rating'])

        # Check if all values in 'user' and 'item' columns are of type str
        self.assertTrue(all(isinstance(user, str) for user in train_df['user']))
        self.assertTrue(all(isinstance(item, str) for item in train_df['item']))
        self.assertTrue(all(isinstance(user, str) for user in val_df['user']))
        self.assertTrue(all(isinstance(item, str) for item in val_df['item']))

        # Check if all values in 'rating' column are of type float
        self.assertTrue(all(isinstance(rating, float) for rating in train_df['rating']))
        self.assertTrue(all(isinstance(rating, float) for rating in val_df['rating']))

if __name__ == '__main__':
    unittest.main()