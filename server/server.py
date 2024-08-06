import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from flask import Flask, jsonify, g, render_template, request
import joblib
from time import time

from model_build.train import predict
from apscheduler.schedulers.background import BackgroundScheduler
from utils.file_utils import read_movie_file, load_properties
from copy import deepcopy
from flask import Response


app = Flask(__name__)
scheduler = BackgroundScheduler()
# Load your model
model = joblib.load('saved_models/updated_best_model.pkl')
model_v2 = joblib.load('saved_models/svd_v2.pkl')

all_movies_list = joblib.load('saved_models/updated_all_movies_list.pkl')
user_movie_list = joblib.load("saved_models/updated_user_movie_list.pkl")

# Metrics tracking variables
total_200_responses = 0
total_non_200_responses = 0
total_response_time = 0.0
slowest_response_time = 0.0
total_responses = 0

def refresh_user_movie_list():
    global user_movie_list
    config = load_properties()
    user_movie_list_file = config.get('MOVIES_WATCHED_FILE_PATH').data
    updated_values = read_movie_file(user_movie_list_file)
    user_movie_list = deepcopy(updated_values)

@app.before_request
def before_request():
    g.request_start_time = time()

@app.after_request
def after_request(response):
    global total_200_responses, total_non_200_responses, total_response_time, slowest_response_time, total_responses
    response_time = time() - g.request_start_time
    total_response_time += response_time
    total_responses += 1
    if response.status_code == 200:
        total_200_responses += 1
    else:
        total_non_200_responses += 1
    if response_time > slowest_response_time:
        slowest_response_time = response_time
    return response

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return jsonify({"status": "UP"}), 200

@app.route('/recommend/<userid>', methods=['GET'])
def recommend(userid):
    try:
        if not userid.isdigit() or not len(userid) > 0:
            return Response("Please enter a valid userId", status=400)

        # Make the predictions
        top_20_items, _ = predict(model, userid, all_movies_list, user_movie_list)

        response = ','.join(str(item) for item in top_20_items)
        return Response(response, status=200)
    except Exception as e:
        return Response("Server error with exception: {}".format(str(e)), status=500)


@app.route('/recommend_v2/<userid>', methods=['GET'])
def recommend_v2(userid):
    try:
        if not userid.isdigit() or not len(userid) > 0:
            return Response("Please enter a valid userId", status=400)

        # Make the predictions
        top_20_items, _ = predict(model_v2, userid, all_movies_list, user_movie_list)

        response = ','.join(str(item) for item in top_20_items)
        return Response(response, status=200)
    except Exception as e:
        return Response("Server error with exception: {}".format(str(e)), status=500)

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if total_responses == 0:
        average_response_time = 0
    else:
        average_response_time = total_response_time / total_responses
    metrics = {
        "200_responses": total_200_responses,
        "non_200_responses": total_non_200_responses,
        "average_response_time": average_response_time*1000,
        "slowest_response_time": slowest_response_time*1000,
    }
    return render_template('dashboard.html', metrics=metrics)


if __name__ == '__main__':
    config = load_properties()
    job1 = scheduler.add_job(refresh_user_movie_list, 'interval', minutes=int(config.get('MOVIES_WATCHED_REFRESH_RATE_MINUTES').data))
    scheduler.start()
    app.run(debug=True, port=8082, host='0.0.0.0')
