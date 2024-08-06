import requests
import os

# Dependency methods
def fetch_movie_details(movie_id):
    response = requests.get(f"http://128.2.204.215:8080/movie/{movie_id}")
    if response.status_code == 200:
        return response.json()
    else:
        return {}

def fetch_user_details(user_id):
    response = requests.get(f"http://128.2.204.215:8080/user/{user_id}")
    if response.status_code == 200:
        return response.json()
    else:
        return {}

# Processing functions
def process_watch_details(log_line, movies_info, users_info):
    parts = log_line.split(',')
    movie_id = parts[2].split('/')[3]
    user_id = parts[1]
    movie_minute = int(parts[2].split('/')[-1].split('.')[0])

    if movie_id not in movies_info:
        movies_info[movie_id] = {"details": fetch_movie_details(movie_id), "num_users": 1, "users": {user_id}}
    else:
        movies_info[movie_id]["users"].add(user_id)
        movies_info[movie_id]["num_users"] = len(movies_info[movie_id]["users"])

    if user_id not in users_info:
        users_info[user_id] = {"details": fetch_user_details(user_id), "movies_watched": {movie_id: {"minutes": movie_minute, "rating": None}}}
    else:
        user_movies = users_info[user_id]["movies_watched"]
        if movie_id in user_movies:
            user_movies[movie_id]["minutes"] += 1
        else:
            user_movies[movie_id] = {"minutes": 1, "rating": None}

def process_rating_details(log_line, movies_info, users_info):
    parts = log_line.split(',')
    movie_id, rating = parts[2].split('/')[2].split('=')
    user_id = parts[1]
    rating = int(rating)

    if movie_id not in movies_info:
        movies_info[movie_id] = {"details": fetch_movie_details(movie_id), "num_users": 0, "users": set()}
    if user_id not in users_info:
        users_info[user_id] = {"details": fetch_user_details(user_id), "movies_watched": {}}

    user_movies = users_info[user_id]["movies_watched"]
    if movie_id in user_movies:
        user_movies[movie_id]["rating"] = rating
    else:
        user_movies[movie_id] = {"minutes": 0, "rating": rating}

import json

# Existing imports and functions remain unchanged

def finalize_and_write_data(movies_info, users_info):
    # Convert user IDs set to list for movies_info
    for movie_id, info in movies_info.items():
        info["users"] = list(info["users"])

    # Replace movie IDs with names in users_info
    for user_id, info in users_info.items():
        movies_watched = {}
        for movie_id, movie_info in info["movies_watched"].items():
            # Assuming the movie details dictionary contains a 'name' key with the movie's name
            # Change 'id' to 'name' if the movie name is stored under a 'name' key
            movie_name = movies_info[movie_id]["details"].get("id", "Unknown")
            movies_watched[movie_name] = movie_info
        info["movies_watched"] = movies_watched

    # Serialize and write the data to JSON files
    with open('data/current/json/movies_m1.json', 'w') as f:
        print("Writing to " + os.path.abspath(f.name))
        json.dump(movies_info, f, indent=4)

    with open('data/current/json/users_m1.json', 'w') as f:
        print("Writing to " + os.path.abspath(f.name))
        json.dump(users_info, f, indent=4)

    print("Data serialization complete and files have been written.")
