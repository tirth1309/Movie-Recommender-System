# Import necessary libraries
from kafka import KafkaConsumer
import requests
import json
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from user_data_generator import convert_csv
from collections import defaultdict
import schedule
import datetime
import time

from data_validation.data_validator import validate_log_line
from process_log_entries import process_watch_details, process_rating_details, finalize_and_write_data
from utils.file_utils import load_properties


def consume_write():

# Kafka topic to consume messages from
    topic = 'movielog5'
    log_buffer = []  # Buffer for log lines
    log_buffer_size = 10000  # Number of lines before flushing to disk
    # Specify number of lines to read from kafka stream
    number_of_lines = 1000000

    # To limit the data collection
    count = 0
    percent = 0
    # Initialize data structures to store aggregated data
    movies_info = {}  # Maps movie_id to a dict with details, number of users, and a set of user IDs
    users_info = {}  # Maps user_id to a dict with user details and a dict of movies watched with details

    # Kafka Consumer Setup
    # Initialize a KafkaConsumer to consume messages from the specified topic
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=["localhost:9092"],  # Kafka server address
        auto_offset_reset="latest",  # Start reading at the earliest message
        enable_auto_commit=True,  # Automatically commit the consumer's offset
        auto_commit_interval_ms=1000,
        #group_id="team05-westworld-train-model"  # Interval between automatic offset commits
    )
    for message in consumer:
        log_line = message.value.decode('utf-8')
        #print(log_line)
        if validate_log_line(log_line):
            if "GET /data/m/" in log_line:
                process_watch_details(log_line, movies_info, users_info)
            elif "GET /rate/" in log_line:
                process_rating_details(log_line, movies_info, users_info)

        #Condition to stop consuming
            count+=1
            if count % (number_of_lines/100) == 0:
                percent+=1
                print(f"Progress: Percentage: {percent}")
            if(count > number_of_lines):
                break

    finalize_and_write_data(movies_info, users_info)

if __name__ == '__main__':
    consume_write()
    convert_csv()
