
from kafka import KafkaConsumer
import datetime

topic = 'movielog5'

LOG_FILE_PATH = "../data/logfile_security.txt"
rating_dict = {}


def monitor():

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        group_id='m4-security',
        enable_auto_commit=True,
        auto_commit_interval_ms=1000
    )

    hasChecked = False
    for message in consumer:
        event = message.value.decode('utf-8')
        values = event.split(',')
        if '/rate/' in values[2]:
            try:
                movie_id, rating = values[2].split('/')[2].split('=')
                rating = int(rating)
                if movie_id not in rating_dict:
                    rating_dict[movie_id] = [rating]
                else:
                    rating_dict[movie_id].append(rating)
            except Exception as e:
                with open(LOG_FILE_PATH, 'a') as file:
                    file.write(f"Error parsing /rate requests: {e}\n")
        
        current_time = datetime.datetime.now()
        if current_time.hour == 12 and hasChecked == False:
            hasChecked = True
            for key, ratings in rating_dict.items():
                if ratings[0] == 1 or ratings[0] == 5:
                    if len(set(ratings)) == 1:
                        with open(LOG_FILE_PATH, 'a') as file:
                            file.write(f"Movie {key} has been attacked\n")
            rating_dict.clear()
        
        elif current_time.hour != 12 and hasChecked == True:
            hasChecked = False

if __name__ == "__main__":
    with open(LOG_FILE_PATH, 'a') as file:
        file.write(f"M4-security Logfile\n")
    monitor()


