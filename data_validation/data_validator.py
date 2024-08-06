# data_validator.py

import re
from datetime import datetime


def is_valid_timestamp(timestamp):
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M'):
        try:
            datetime.strptime(timestamp, fmt)
            return True
        except ValueError:
            continue
    return False

def is_valid_user_id(user_id):
    return user_id.isdigit() and len(user_id) > 0


def validate_action_format(action):
    """
    Validate that the action part of the log line follows expected formats for watch, rate, or recommendation actions.
    Checks that movie watch actions do not contain spaces before the .mpg extension.
    """
    watch_pattern = re.compile(r"GET /data/m/.+/\d+\.mpg$")
    rate_pattern = re.compile(r"GET /rate/.+=\d$")
    recommendation_pattern = re.compile(r"recommendation request .+, status 200, result: .+")

    if "GET /data/m/" in action:
        if not watch_pattern.match(action) or " " in action.split('/')[-1]:
            return False  # Reject if there's a space or if it doesn't match the pattern

    elif "GET /rate/" in action:
        if not rate_pattern.match(action):
            return False  # Reject if it doesn't match the pattern

    elif "recommendation request" in action:
        if not recommendation_pattern.match(action):
            return False  # Reject if it doesn't match the pattern

    else:
        return False  # Reject if it doesn't match any known action pattern

    return True


def validate_recommendation_result(action):
    if "recommendation request" in action:
        try:
            # Extracting the recommendation result and processing time
            result_string = action.split("result: ")[1]
            movies_list, processing_time = result_string.rsplit(", ", 1)

            # Validate processing time format (e.g., "210 ms")
            if not re.match(r"\d+ ms", processing_time):
                return False

            # Split the movies list and convert it to a set to ensure uniqueness
            movies = movies_list.split(", ")
            # Check that there are exactly 20 unique recommended movies
            return len(set(movies)) == 20
        except (IndexError, ValueError):
            return False
    return True


def validate_log_line(log_line):
    parts = log_line.split(',')
    if len(parts) < 3:
        return False
    timestamp, user_id, action = parts[0], parts[1], ','.join(parts[2:])

    # Timestamp and user ID validations remain unchanged
    if not is_valid_timestamp(timestamp) or not is_valid_user_id(user_id):
        return False

    # Action format validation
    if not validate_action_format(action):
        return False

    if "GET /data/m/" in action:
        # Validate .mpg extension presence for movie watch actions
        if not action.endswith(".mpg"):
            return False  # Invalid if the action does not end with .mpg

    # Validate rating values specifically for rate actions
    if "GET /rate/" in action:
        _, rating = action.split('/')[2].split('=')
        if not 1 <= int(rating) <= 5:  # Ensuring rating is within a 1-5 range
            return False

    # Additional recommendation result validation for recommendation actions
    if not validate_recommendation_result(action):
        return False

    return True
