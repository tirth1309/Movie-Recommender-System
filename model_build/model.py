from surprise import Dataset
from surprise import Reader
from surprise import KNNWithMeans
from surprise import SVD, SVDpp, KNNBasic, NMF,SlopeOne,CoClustering

def prepare_data_for_recommendation_model(train_df, val_df, rating_range=(1, 5)):
    """
    Given the train_df, val_df from the prepare_data method and the ratings range (whose default is 1 to 5),
    this returns the data in a surprise package models understandable format
    """
    train_reader = Reader(rating_scale=rating_range)
    val_reader = Reader(rating_scale=rating_range)

    train_data = Dataset.load_from_df(train_df[["user", "item", "rating"]], train_reader)
    valid_data = Dataset.load_from_df(val_df[["user", "item", "rating"]], val_reader)

    return train_data, valid_data

def build_model(model_name, similarity_options=None, **kwargs):
    """
    Given a model name, similarity options (applicable for Kmeans based models), and additional parameters in the
    form of kwargs, it builds the model object and returns it
    """

    models_dict = {
        'KNNWithMeans': KNNWithMeans,
        'KNNBasic': KNNBasic,
        'SVDpp': SVDpp,
        'SVD': SVD,
        'NMF': NMF,
        'CoClustering': CoClustering,
        'SlopeOne': SlopeOne,
    }

    if model_name in models_dict:
        if similarity_options is not None:
            return models_dict[model_name](sim_options=similarity_options, **kwargs)
        else:
            return models_dict[model_name](**kwargs)
    raise Exception("Unrecognized model name passed. Please send one among ['KNNWithMeans', 'KNNBasic', 'SVDpp', 'SVD', 'NMF', 'CoClustering', 'SlopeOne']")
