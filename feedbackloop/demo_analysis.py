import requests
from collections import defaultdict
def fetch_user_details(user_id):
    response = requests.get(f"http://128.2.204.215:8080/user/{user_id}")
    if response.status_code == 200:
        return response.json()
    else:
        return {}

logs = open("logfile_backup.txt", "r").readlines()
users = set()
for log in logs:
    user = log.split(",")[1].strip()
    users.add(user)
    if len(users) > 10000:
        break

gender = {'M': 0, 'F': 0}
ages = defaultdict(int)
import json
user_details = open("user_details.txt", "r").readlines()
for user in user_details:
    user_json = json.loads(user.strip())
    gender[user_json['gender']] += 1
    ages[int(user_json['age']/10)] += 1
print(gender)
print(ages)


for i, user in enumerate(users):
    if i % 500 == 0:
        print("Done: ", i)
        user_details.flush()
    details = fetch_user_details(user)
    user_details.write(f"{str(details)}\n")

print(len(users))