import pandas as pd
import json


def prepare_data_from_json(file_path):
    """
    This function returns two dfs: train_df - this contains the first 80% of the non missing entries for each user;
    val_df contains the bottom 20% of the non missing entries for each user
    :param file_path: complete data json file path
    :return: train_df, val_df
    """

    json_file = open(file_path)
    data = json.load(json_file)
    users = data.keys()

    ratings_dict = {
        'item': [],
        'user': [],
        'rating': [],
    }

    validation_ratings_dict = {
        'item': [],
        'user': [],
        'rating': [],
    }

    total_missing_rating_movies = 0
    for user in users:
        movies = data[user]['movies_watched']
        filteredmovies = {movie: movies[movie] for movie in movies if movies[movie]['rating'] is not None}
        total_missing_rating_movies += (len(movies) - len(filteredmovies))
        for i, movie in enumerate(filteredmovies):
            if i < 0.8 * len(filteredmovies):
                rating = filteredmovies[movie]['rating']
                ratings_dict['item'].append(movie)
                ratings_dict['user'].append(user)
                ratings_dict['rating'].append(rating)
            else:
                rating = filteredmovies[movie]['rating']
                validation_ratings_dict['item'].append(movie)
                validation_ratings_dict['user'].append(user)
                validation_ratings_dict['rating'].append(rating)

    train_df = pd.DataFrame(ratings_dict)
    val_df = pd.DataFrame(validation_ratings_dict)
    return train_df, val_df


def prepare_data_from_csv(file_path):
    """
    This function returns two dataframes: train_df - this has the first 80% of entries for each user; val_df - this has
    the bottom 20% of entries for each user
    :param file_path: complete data csv file path
    :return: train_df, val_df
    """

    df = pd.read_csv(file_path)

    df['cumulative_count'] = df.groupby('User_ID').cumcount()
    df['80_percent_index'] = df.groupby('User_ID')['cumulative_count'].transform(lambda x: int(0.8 * x.max()))

    train_df = df[df['cumulative_count'] <= df['80_percent_index']].drop(['cumulative_count', '80_percent_index'], axis=1)
    val_df = df[df['cumulative_count'] > df['80_percent_index']].drop(['cumulative_count', '80_percent_index'], axis=1)

    train_df.reset_index(drop=True, inplace=True)
    val_df.reset_index(drop=True, inplace=True)

    train_df = train_df[['User_ID', 'Movie_Ids', 'Movie_Rating']]
    train_df.columns = ['user', 'item', 'rating']

    val_df = val_df[['User_ID', 'Movie_Ids', 'Movie_Rating']]
    val_df.columns = ['user', 'item', 'rating']

    train_df['user'] = train_df['user'].astype(str)
    train_df['item'] = train_df['item'].astype(str)
    train_df['rating'] = train_df['rating'].astype(float)

    val_df['user'] = val_df['user'].astype(str)
    val_df['item'] = val_df['item'].astype(str)
    val_df['rating'] = val_df['rating'].astype(float)

    return train_df, val_df