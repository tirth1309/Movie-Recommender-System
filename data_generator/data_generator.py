# Import necessary libraries
from kafka import KafkaConsumer
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from collections import defaultdict
import datetime
import time
from flask import Flask, jsonify, g, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler()

from data_validation.data_validator import validate_log_line
from utils.file_utils import load_properties

movies_info = {}  # Maps movie_id to a dict with details, number of users, and a set of user IDs
users_info = {}  # Maps user_id to a dict with user details and a dict of movies watched with details

config = load_properties()

def merge_dict_lists(dict1, dict2):
    for key, value_set in dict2.items():
        if key in dict1:
            dict1[key].update([i for i in value_set])
        else:
            dict1[key] = value_set
    
def flush_to_disk(path, dict):
    print("write to file {}".format(path))
    try:
        with open(path, 'r') as file:
            prev_records = file.readlines()
        prev_records_dict = { i.split(",")[0]: set([j.strip() for j in i.split(",")[1:]]) for i in prev_records }
        merge_dict_lists(prev_records_dict, dict)
        result = [i + ", " + ", ".join([k for k in j]) + "\n" for i, j in prev_records_dict.items()]
        with open(path, 'w') as file:
            file.writelines(result)
    except FileNotFoundError:
        result = [i + ", " + ", ".join([k for k in j]) + "\n" for i, j in dict.items()]
        with open(path, 'w') as file:
            file.writelines(result)

def buffered_write_to_disk(path, buffer):
    """Write buffered data to disk."""
    with open(path, "a") as file:
        file.writelines(buffer)
    buffer.clear()

def check_ab_experiment():
    flag = int(open(config.get("AB_FLAG_STORE_DATA_GENERATOR").data, "r").read())
    return flag

def begin_ab_experiment():
    fi = open(config.get("AB_FLAG_STORE_DATA_GENERATOR").data, "w")
    fi.write("1")
    fi.close()
    open(config.get('AB_MOVIES_WATCHED_FILE_PATH').data, "w").close()
    open(config.get('AB_MOVIES_RECOMMENDED_FILE_PATH').data, "w").close()

def end_ab_experiment():
    fi = open(config.get("AB_FLAG_STORE_DATA_GENERATOR").data, "w")
    fi.write("0")
    fi.close()

def write_log_entry(log_entry, final_flush, count, watched_movies, recommended_movies):
    tokens = log_entry.strip().split(",")
    user_id = tokens[1]
    if len(tokens) == 3 and tokens[2][5:9] == "data":
        # watch
        movie_id = tokens[2].split("/")[3].strip()
        watched_movies[user_id].add(movie_id)
    elif len(tokens) > 3:
        # recommend
        tokens[4] = tokens[4].split(":")[1].strip()  # remove 'result:'
        recommended_movies[user_id].update([i.strip() for i in tokens[4:-1]])
    if count >= 10000 or final_flush == 'Y':
        print('Inside flush')
        flush_to_disk(config.get('MOVIES_WATCHED_FILE_PATH').data, watched_movies)
        flush_to_disk(config.get('MOVIES_RECOMMENDED_FILE_PATH').data, recommended_movies)

        if check_ab_experiment() == 1:
            flush_to_disk(config.get('AB_MOVIES_WATCHED_FILE_PATH').data, watched_movies)
            flush_to_disk(config.get('AB_MOVIES_RECOMMENDED_FILE_PATH').data, recommended_movies)

        watched_movies = defaultdict(set)
        recommended_movies = defaultdict(set) 

def consume_write():

# Kafka topic to consume messages from
    topic = 'movielog5'
    log_buffer = []  # Buffer for log lines
    log_buffer_size = 10000  # Number of lines before flushing to disk
    # Specify number of lines to read from kafka stream
    number_of_lines = 30000000

    # To limit the data collection
    count = 0
    percent = 0
    watched_movies = defaultdict(set)
    recommended_movies = defaultdict(set)

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
        group_id="team05-westworld-test-cg"  # Interval between automatic offset commits
    )

        
    # Main loop to process messages from Kafka
    for message in consumer:
        log_line = message.value.decode('utf-8')

        if not validate_log_line(log_line):
            # If invalid, write to the error file and skip further processing
            with open(config.get('ERROR_LOG_FILE_PATH').data, "a") as err_file:
                err_file.write(log_line + "\n")
            continue

        log_buffer.append(log_line + "\n")

        # Flush log buffer to disk when it reaches a certain size
        if len(log_buffer) >= log_buffer_size:
            buffered_write_to_disk(config.get('LOG_FILE_PATH').data, log_buffer)

        count = count + 1
        write_log_entry(log_line, 'N', count, watched_movies, recommended_movies)
        if count >= 10000:
            count = 0

        # if "GET /data/m/" in log_line:
        #     process_watch_details(log_line, movies_info, users_info)
        # elif "GET /rate/" in log_line:
        #     process_rating_details(log_line, movies_info, users_info)

    # Condition to stop consuming
        #count+=1
        # if count % (number_of_lines/100) == 0:
        #     percent+=1
        #     print(f"Progress: Percentage: {percent}")
        # if(count > number_of_lines):
        #     break
        current_time = datetime.datetime.now()
        if current_time.minute >= 30:
            write_log_entry(log_line, 'Y', count, watched_movies, recommended_movies)
            buffered_write_to_disk(config.get('LOG_FILE_PATH').data, log_buffer)
            break

    #finalize_and_write_data(movies_info, users_info)

@app.route('/abexperiment', methods=['POST'])
def abexperiment():
    ab_expt_flag = request.json['abExperimentFlag']
    if ab_expt_flag is True or ab_expt_flag == "true":
        begin_ab_experiment()
    else:
        end_ab_experiment()
    return {"success": True}, 200

#convert_csv()
if __name__ == '__main__':
    print("Started Data generation service....")
    scheduler.add_job(consume_write, trigger='cron', hour='*')
    scheduler.start()
    app.run(debug=True, port=8077, host='0.0.0.0')
