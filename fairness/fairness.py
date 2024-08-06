import json
import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Assuming 'movies_m1.json' contains a dictionary of movies, each with their own nested details
# Read the JSON file
with open('data/current/json/movies_m1.json', 'r') as file:
    movies_data = json.load(file)

# Initialize an empty list to hold all processed movie data
all_movies_processed = []

# Loop through each movie entry in the JSON data
for movie_id, movie_info in movies_data.items():
    # Process each movie's details
    movie_details = movie_info['details']
    processed_data = {
        'id': movie_details.get('id', ''),
        'adult': movie_details.get('adult', ''),
        'genres_name': ', '.join([genre['name'] for genre in movie_details.get('genres', [])]),
        'popularity': movie_details.get('popularity', ''),
        'spoken_languages': ', '.join([lang['name'] for lang in movie_details.get('spoken_languages', [])]),
        'status': movie_details.get('status', ''),
        'vote_average': movie_details.get('vote_average', ''),
        'vote_count': movie_details.get('vote_count', ''),
    }
    all_movies_processed.append(processed_data)

# Create a DataFrame from the processed movie data
df_movies = pd.DataFrame(all_movies_processed)
# Write the DataFrame to a CSV file
csv_output_path = 'data/current/csv/movies_m1.csv'
df_movies.to_csv(csv_output_path, index=False)

users_data_df = pd.read_csv('data/current/csv/user_data_1.csv')
movies_data_df = pd.read_csv('data/current/csv/movies_m1.csv')
users_data_df['User_ID'] = users_data_df['User_ID'].astype('Int64')
movies_data_df['vote_count'] = movies_data_df['vote_count'].astype('Int64')
users_data_df['Movie_Duration'] = users_data_df['Movie_Duration'].astype('Int64')
users_data_df['Movie_Rating'] = users_data_df['Movie_Rating'].astype('Int64')


# Perform the join operation on 'Movie_Ids' from users_data_df and 'id' from movies_data_df
merged_df = pd.merge(users_data_df, movies_data_df, left_on='Movie_Ids', right_on='id')

# Write the merged DataFrame to a new CSV file
merged_csv_output_path = 'data/current/csv/merged_users_movies.csv'
merged_df.to_csv(merged_csv_output_path, index=False)
