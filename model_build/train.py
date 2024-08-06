import joblib, os
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from collections import defaultdict

from model_build.model import *
from model_build.prepare_data import *
from surprise import accuracy
import time
from utils.file_utils import load_properties
import argparse

# all_movies_list = joblib.load('saved_models/updated_all_movies_list.pkl')
# user_movie_list = joblib.load("saved_models/updated_user_movie_list.pkl")

# all_movies_list = []
# user_movie_list = defaultdict(set)

def train(training_args):
    """
    Prepares the data, builds the model, and performs training, finally returns the trained model
    """

    global all_movies_list, user_movie_list
    model_name = training_args['model_name']
    similarity_options = training_args.get('similarity_options', None)
    file_path = training_args['file_path']
    is_csv = 'csv' in file_path
    if is_csv:
        train_df, val_df = prepare_data_from_csv(file_path)
    else:
        train_df, val_df = prepare_data_from_json(file_path)
    additional_args = training_args.get('model_specific_args', None)

    all_movies_list = train_df['item'].unique().tolist()
    temp_user_movie_list = defaultdict(set)
    for i, row in train_df.iterrows():
        user = row['user']
        item = row['item']
        temp_user_movie_list[user].add(item)
    user_movie_list = temp_user_movie_list.copy()

    train_data, valid_data = prepare_data_for_recommendation_model(train_df, val_df)
    model = build_model(model_name, similarity_options=similarity_options, **additional_args if additional_args else {})

    trainingSet = train_data.build_full_trainset()
    model.fit(trainingSet)
    if training_args.get('return_user_movie_list', False):
        return model, train_data, valid_data, train_df, val_df, user_movie_list, all_movies_list
    return model, train_data, valid_data, train_df, val_df

def evaluate(model, valid_data):
    """
    Given validation data returned in the above train function, evaluate the RMSE score
    """
    validationset = [(uid, iid, r) for (uid, iid, r, _) in valid_data.raw_ratings]
    predictions = model.test(validationset)
    rmse = accuracy.rmse(predictions)
    return rmse
#
def predict(model, user_id, all_movies_list, user_movie_list, K=20, return_time=False):
    """
    This is the inference function. Given a user id, trained model, number of predictions you need (parameter K),
    return_time denoting whether you want to compute the time or not, returns the top K recommendations
    """

    # global all_movies_list
    # global user_movie_list
    start = time.time() if return_time else None
    scores = []
    recommendations = []

    for movie in all_movies_list:
        if user_id in user_movie_list and movie in user_movie_list[user_id]:
            continue
        prediction = model.predict(uid=user_id, iid=movie)
        scores.append((prediction.est, movie))

    scores.sort(reverse=True)
    count = 0
    for i, movie in scores:
        count += 1
        recommendations.append(movie)
        if count >= K:
            break

    time_taken = time.time() - start if return_time else None
    return recommendations, time_taken

def retrain_model():
    config = load_properties()
    model_name = config.get('MODEL_NAME').data
    print("Inside retrain model")
    training_args = {
        'model_name': model_name,
        'file_path': 'data/current/csv/user_data_1.csv',
        'return_user_movie_list': True,
    }
    model, train_data, valid_data, train_df, val_df, user_movie_list, all_movies_list = train(training_args)
    os.rename('saved_models/updated_best_model.pkl', 'saved_models/previous_best_model.pkl')
    os.rename('saved_models/updated_all_movies_list.pkl', 'saved_models/old_all_movies_list.pkl')
    os.rename("saved_models/updated_user_movie_list.pkl", "saved_models/old_user_movie_list.pkl")
    joblib.dump(model, 'saved_models/updated_best_model.pkl')
    joblib.dump(all_movies_list, "saved_models/updated_all_movies_list.pkl")
    joblib.dump(user_movie_list, "saved_models/updated_user_movie_list.pkl")


training_args = [{
    'model_name': 'SVD',
    # 'similarity_options': {
    #     "name": "cosine",
    #     "user_based": False,
    # },
    'file_path': 'data/user_data_2.csv',
    # "model_specific_args": {
    #         'n_epochs': 10,
    #         'reg_all': 0.1,
    #         'lr_all': 0.01,
    #         'init_std_dev': 0.01,
    #     }
    },
    {
    'model_name': 'KNNWithMeans',
    'similarity_options': {
        "name": "cosine",
        "user_based": True,
    },
    'file_path': 'data/user_data_2.csv',
    "model_specific_args": {
        'k': 20,
        'min_k': 5,
    }
}]

def findBestModel(training_args):

    rmse_score = 100
    model, train_data, valid_data, train_df, val_df = train(training_args[0])
    for training_arg in range(1, len(training_args)):
        model_new, train_data_new, valid_data_new, train_df_new, val_df_new = train(training_args[training_arg])
        rmse_score_new = evaluate(model_new, valid_data_new)

        print("Validation RMSE value is {}".format(str(rmse_score_new)))
        if rmse_score_new < rmse_score:
            model, train_data, valid_data, train_df, val_df = model_new, train_data_new, valid_data_new, train_df_new, val_df_new
            rmse_score = rmse_score_new

    print("Best Validation RMSE value is {}".format(str(rmse_score)))
    return model, train_data, valid_data, train_df, val_df, user_movie_list

# train_start = time.time()
# model, train_data, valid_data, train_df, val_df = train(training_args[0])
# print("Total time taken for training is {}".format(str(time.time()-train_start)))


# rmse_score = evaluate(model, valid_data)
# print("Validation RMSE value is {}".format(str(rmse_score)))
#
# for training_arg in range(1, len(training_args)):
#     model_new, train_data_new, valid_data_new, train_df_new, val_df_new = train(training_args[training_arg])
#     rmse_score_new = evaluate(model_new, valid_data_new)
#     print("Validation RMSE value is {}".format(str(rmse_score_new)))
#     if rmse_score_new > rmse_score:
#         model, train_data, valid_data, train_df, val_df, user_movie_list = model_new, train_data_new, valid_data_new, train_df_new, val_df_new, user_movie_list
#         rmse_score = rmse_score_new


# model = joblib.load('saved_models/updated_best_model.pkl')
# file_size_bytes = os.path.getsize('saved_models/updated_best_model.pkl')
#
# file_size_kb = file_size_bytes / 1024
# file_size_mb = file_size_kb / 1024
# print("Size of the model in MB is: {}".format(str(file_size_mb)))

# if not os.path.exists('saved_models/updated_best_model.pkl'):
#     joblib.dump(model, 'saved_models/updated_best_model.pkl')
#     joblib.dump(all_movies_list, "saved_models/updated_all_movies_list.pkl")
#     joblib.dump(user_movie_list, "saved_models/updated_user_movie_list.pkl")

# print("Best Validation RMSE value is {}".format(str(rmse_score)))

# test_user = "190296"
# test_user = "126558"
# test_user = "16507000"
# recommendations, time_taken = predict(model, test_user, K=20, return_time=True)
# print("Top 20 recommendations for user: {} are: {} and the time taken is {}".format(test_user, str(recommendations), str(time_taken) if time_taken else "Not calculated"))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--retrain', action='store_true', default=False, help='retrain the model')
    args = parser.parse_args()
    print(args)
    if args.retrain:
        retrain_model()
