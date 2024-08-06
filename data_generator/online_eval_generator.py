
import os, json, time
from collections import defaultdict

# check the target logfile periodically, if it has been modified, parse the new entries and update the the 2 json files

def parse_logfile(log_entries, watched_movies, recommended_movies):
    for entry in log_entries:
        if entry.strip() == "":
            continue
        tokens = entry.strip().split(",")
        user_id = tokens[1]
        if len(tokens) == 3 and tokens[2][5:9] == "data":
            # watch
            movie_id = tokens[2].split("/")[3].strip()
            watched_movies[user_id].add(movie_id) 
        elif len(tokens) > 3:
            # recommend
            tokens[4] = tokens[4].split(":")[1].strip()  # remove 'result:'
            recommended_movies[user_id].update([i.strip() for i in tokens[4:-1]])
            

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
            
    
def main_loop(path, interval=10):
    watched_movies = defaultdict(set)
    recommended_movies = defaultdict(set)
    last_size = 0
    
    while True:
        try:
            current_size = os.stat(path).st_size
        except FileNotFoundError:
            print("File not found. Will retry.")
            time.sleep(60)
            continue
        
        if current_size > last_size:
            with open(path, 'r') as file:
                if current_size > last_size:
                    file.seek(last_size)
                    parse_logfile(file.readlines(), watched_movies, recommended_movies)
                    flush_to_disk("../data/watched_movies.txt", watched_movies)
                    flush_to_disk("../data/recommended_movies.txt", recommended_movies)
                    last_size = file.tell()
                    watched_movies.clear()
                    recommended_movies.clear()
                    
        time.sleep(interval)
        print("sleeping...")


if __name__ == "__main__":
    main_loop("../data/log1.txt")
