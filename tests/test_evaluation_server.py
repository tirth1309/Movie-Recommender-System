import unittest
from unittest.mock import MagicMock, patch
import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.evaluation_server import refresh_online_evaluation_metrics


class TestRefreshOnlineEvaluationMetrics(unittest.TestCase):
    def setUp(self):
        # Mocking the get_online_evaluation_statistics function
        self.get_online_evaluation_statistics = MagicMock(return_value=(0.8, 0.9, 0.85, 0.88, 1))
        # Patching the get_online_evaluation_statistics function with the mock
        self.patcher = patch('server.evaluation_server.get_online_evaluation_statistics', self.get_online_evaluation_statistics)
        self.patcher.start()

    def tearDown(self):
        # Stopping the patcher
        self.patcher.stop()

    def test_refresh_online_evaluation_metrics(self):
        macro_precision, macro_recall, micro_precision, micro_recall, value_last_recorde, recommendation_adoption = refresh_online_evaluation_metrics()

        # Assertions
        self.assertEqual(macro_precision, 0.8)
        self.assertEqual(macro_recall, 0.9)
        self.assertEqual(micro_precision, 0.85)
        self.assertEqual(micro_recall, 0.88)


if __name__ == '__main__':
    unittest.main()