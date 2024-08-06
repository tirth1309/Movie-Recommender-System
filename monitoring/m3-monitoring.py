
from kafka import KafkaConsumer
from prometheus_client import Counter, Histogram, start_http_server
import os
import time
import datetime

topic = 'movielog5'

LOG_FILE_PATH = "../data/logfile_m4.txt"
MOVIES_WATCHED_FILE_PATH = '../data/watched_movies.txt'
MOVIES_RECOMMENDED_FILE_PATH = '../data/recommended_movies.txt'  

start_http_server(8765)

# Metrics like Counter, Gauge, Histogram, Summaries
# Refer https://prometheus.io/docs/concepts/metric_types/ for details of each metric
#  (a) service availability
REQUEST_COUNT = Counter(
    'request_count', 'Recommendation Request Count',
    ['http_status']
)
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')

# (b) model accuracy. 
MACRO_PRECISION = Histogram('macro_precision', 'macro precision rate')
MACRO_RECALL = Histogram('macro_recall', 'macro recall rate')
MICRO_PRECISION = Histogram('micro_precision', 'micro precision rate')
MICRO_RECALL = Histogram('micro_recall', 'micro recall rate')
RECOMMENDATION_ADOPTION = Histogram('recommendation_adoption', 'recommendation adoption rate')

def read_movie_file(path):
    lines = open(path, 'r').readlines()
    movie_data = {}
    for line in lines:
        items = line.strip().split(',')
        movies = [item.strip() for item in items[1:]]
        movie_data[items[0]] = set(movies)
    return movie_data

def get_accuracy_metrics():
    # reuse m2 online evaluation code
    movies_watched_data = read_movie_file(MOVIES_WATCHED_FILE_PATH)
    movies_recommended_data = read_movie_file(MOVIES_RECOMMENDED_FILE_PATH)
    macro_precision, macro_recall, micro_precision, micro_recall, total_recommendations, total_movies_watched = 0, 0, 0, 0, 0, 0
    at_least_one_recommended_watched = 0

    for user in movies_recommended_data:
        recommendations = set(movies_recommended_data[user])
        movies_watched = set(movies_watched_data.get(user, []))
        precision_intersection = len(recommendations.intersection(movies_watched))
        recall_intersection = len(movies_watched.intersection(recommendations))
        precision, recall = 0, 0
        if len(recommendations):
            precision = precision_intersection / len(recommendations)
        if len(movies_watched):
            recall = recall_intersection / len(movies_watched)
        if precision_intersection > 0:
            at_least_one_recommended_watched += 1
        macro_precision += precision
        macro_recall += recall

        micro_precision += precision_intersection
        micro_recall += recall_intersection
        total_recommendations += len(recommendations)
        total_movies_watched += len(movies_watched)
        
        current_time = datetime.datetime.now()
        if current_time.minute >= 55:
            break

    macro_precision = macro_precision / len(movies_recommended_data)
    macro_recall = macro_recall / len(movies_recommended_data)
    if total_recommendations:
        micro_precision = micro_precision / total_recommendations
    else:
        micro_precision = 0
    if total_movies_watched:
        micro_recall = micro_recall / total_movies_watched
    else:
        micro_recall = 0
    recommendation_adoption = at_least_one_recommended_watched / len(movies_recommended_data)
    return (macro_precision, macro_recall, micro_precision, micro_recall, recommendation_adoption)
        
def monitor():
    counter = 0
    
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        group_id='m3-monitoring',
        enable_auto_commit=True,
        auto_commit_interval_ms=1000
    )

    for message in consumer:
        event = message.value.decode('utf-8')
        values = event.split(',')
        # availability metric
        if 'recommendation request' in values[2]:
            counter += 1
            if 'status 200' in values[3]:
                # print(event)
                REQUEST_COUNT.labels(http_status=200).inc()
                time_taken = float(values[-1].strip().split(" ")[0])
                REQUEST_LATENCY.observe(time_taken / 1000)
            else: 
                print(event)
                REQUEST_COUNT.labels(http_status=400).inc()
                
        # accuracy metric
        if (counter >= 300):
            # an interval different from the data generation service write
            current_time = datetime.datetime.now()
            if current_time.minute >= 1 and current_time.minute <= 59:
                counter = 0
                macro_precision, macro_recall, micro_precision, micro_recall, recommendation_adoption = get_accuracy_metrics()
                MACRO_PRECISION.observe(macro_precision)
                MACRO_RECALL.observe(macro_recall)
                MICRO_PRECISION.observe(micro_precision)
                MICRO_RECALL.observe(micro_recall)
                RECOMMENDATION_ADOPTION.observe(recommendation_adoption)
                print(macro_precision, macro_recall, micro_precision, micro_recall, recommendation_adoption)
                
            
if __name__ == "__main__":
    monitor()


