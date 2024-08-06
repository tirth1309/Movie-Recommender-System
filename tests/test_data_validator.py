# test_data_validator.py
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pytest
from data_validation.data_validator import is_valid_timestamp, is_valid_user_id, validate_action_format, validate_recommendation_result, validate_log_line

# Timestamp validation tests
@pytest.mark.parametrize("timestamp,expected", [
    ("2023-01-01T12:00:00", True),
    ("2023-01-01T12:00", True),
    ("2023-01-01T12:00:00.123456", True),
    ("2023/01/01T12:00:00", False),
    ("01-01-2023T12:00:00", False),
    ("2023-01-01 12:00:00", False),
])
def test_is_valid_timestamp(timestamp, expected):
    assert is_valid_timestamp(timestamp) == expected

# User ID validation tests
@pytest.mark.parametrize("user_id,expected", [
    ("12345", True),
    ("0", True),
    ("", False),
    ("abc123", False),
])
def test_is_valid_user_id(user_id, expected):
    assert is_valid_user_id(user_id) == expected

# Action format validation tests
@pytest.mark.parametrize("action,expected", [
    ("GET /data/m/movie/1234.mpg", True),
    ("GET /data/m/movie 1234.mpg", False),
    ("GET /rate/movie=5", True),
    ("recommendation request, status 200, result: Movie1, Movie2, 210 ms", False),
    ("GET /unknown/action", False),
])
def test_validate_action_format(action, expected):
    assert validate_action_format(action) == expected

# Recommendation result validation tests
@pytest.mark.parametrize("action,expected", [
    ("recommendation request movie, status 200, result: " + ", ".join([f"Movie{i}" for i in range(20)]) + ", 210 ms", True),
    ("recommendation request movie, status 200, result: Movie1, Movie1, 210 ms", False),
    ("GET /data/m/movie/1234.mpg", True),
])
def test_validate_recommendation_result(action, expected):
    assert validate_recommendation_result(action) == expected

# Log line validation tests
@pytest.mark.parametrize("log_line,expected", [
    ("2023-01-01T12:00:00,12345,GET /data/m/movie/1234.mpg", True),
    ("2023-01-01T12:00:00,12345,GET /rate/movie=5", True),
    ("2023-01-01T12:00:00,12345,GET /rate/movie=6", False),
    ("invalid_timestamp,12345,GET /data/m/movie/1234.mpg", False),
    ("2023-01-01T12:00:00,abc,GET /data/m/movie/1234.mpg", False),
    ("2023-01-01T12:00:00,12345,recommendation request movie, status 200, result: " + ", ".join([f"Movie{i}" for i in range(19)]) + ", 210 ms", False),
])
def test_validate_log_line(log_line, expected):
    assert validate_log_line(log_line) == expected
