from flask import Flask, request, Response
import requests
import configparser
from utils.file_utils import load_properties
from time import time
import subprocess
import re
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
app = Flask(__name__)

# Load configurations from properties file
config = load_properties();

FORWARD_URL = config.get('FORWARD_URL').data # PORT MISSING IN CONFIG ?
SECONDARY_URL = config.get('SECONDARY_URL').data
TOP_MOVIES = config.get('TOP_MOVIES').data
# AB_TEST = config.get('AB_TEST').data


def get_user_id():
    return request.view_args.get('userId', 'anonymous')


limiter = Limiter(
    get_user_id,
    app=app,
    headers_enabled=True  # To send rate limit info in headers
)

# print(FORWARD_URL)
# print(SECONDARY_URL)
# print(TOP_MOVIES)
version = ""


def data_versioning():
    with open('data/current/csv/user_data_1.csv.dvc', 'r') as file:
        # Read the content of the file
        lines = file.readlines()

    # Extract and format the values
    values = []
    values.append("Data Versioning: ")
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        # Split the line by ':' and extract the key and value
        key, value = map(str.strip, line.split(':'))
        values.append(f"{key}: {value}")

    repo_url = 'https://github.com/cmu-seai/group-project-s24-team-5-westworld'
    process = subprocess.Popen(["git", "ls-remote", repo_url], stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    sha = re.split(r'\t+', stdout.decode('ascii'))[0]
    key = "Commitid"
    values.append(f"{key}: {sha}")

    values.append("Model Versioning: ")
    with open('saved_models/updated_best_model.pkl.dvc', 'r') as file:
        # Read the content of the file
        lines = file.readlines()

    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        # Split the line by ':' and extract the key and value
        key, value = map(str.strip, line.split(':'))
        values.append(f"{key}: {value}")

    # Print the values as a single line
    print("Recommended model from: " + ', '.join(values))
    return "Recommended model from: " + ', '.join(values)

def check_ab_experiment():
    flag = int(open(config.get("AB_FLAG_STORE_LOAD_BALANCER").data, "r").read())
    return flag

def begin_ab_experiment():
    fi = open(config.get("AB_FLAG_STORE_LOAD_BALANCER").data, "w")
    fi.write("1")
    fi.close()
    requests.post(config.get('DATA_GENERATOR_URL').data, json={'abExperimentFlag': True}, headers={'Content-Type': 'application/json'})


def end_ab_experiment():
    fi = open(config.get("AB_FLAG_STORE_LOAD_BALANCER").data, "w")
    fi.write("0")
    fi.close()
    requests.post(config.get('DATA_GENERATOR_URL').data, json={'abExperimentFlag': False}, headers={'Content-Type': 'application/json'})

@app.route('/recommend/<userId>')
@limiter.limit("60 per minute", error_message="You are being rate limited")
def recommend(userId):
    try:
        if not userId.isdigit() or not len(userId) > 0:
            return Response("Please enter a valid userId", status=400)
        config = load_properties();
        # Determine URL based on AB testing switch and userId
        url_to_use = config.get('FORWARD_URL').data
        if check_ab_experiment() == 1:
            if int(userId) % 2 == 0:  # Even userId
                print("Using Secondary URL")
                url_to_use = config.get('SECONDARY_URL').data
        response = requests.get(f"{url_to_use}/{userId}", timeout=0.4)
        print(version)
        if response.status_code == 200:
            return response.text
        else:
            print("Status_code:", response.status_code)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, ValueError):
        print("Took Long or Invalid UserId")
        pass

    return TOP_MOVIES


@app.route('/abexperiment', methods=['POST'])
def abexperiment():
    ab_expt_flag = request.json['abExperimentFlag']
    if ab_expt_flag is True or ab_expt_flag == "true":
        begin_ab_experiment()
    else:
        end_ab_experiment()
    return {"success": True}, 200

if __name__ == '__main__':
    version = data_versioning()
    versioning_file = open(config.get("PREDICTION_SERVICE_VERSIONING_FILE").data, "a")
    versioning_file.write(str(time()) + "\t" + version + "\n")
    versioning_file.close()
    app.run(debug=True, port=8082, host='0.0.0.0')
