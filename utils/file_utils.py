from jproperties import Properties
import os

def read_movie_file(path):
    lines = open(path, 'r', encoding='utf-8').readlines()
    movie_data = {}
    for line in lines:
        items = line.strip().split(',')
        movies = [item.strip() for item in items[1:]]
        movie_data[items[0]] = set(movies)
    return movie_data

# def load_properties():
#     configs = Properties()
#     with open('project.properties', 'rb') as read_prop:
#         configs.load(read_prop)
#     return configs

def load_properties():
    configs = Properties()
    # Calculate the absolute path to the root of the project
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    properties_path = os.path.join(project_root, 'project.properties')
    
    with open(properties_path, 'rb') as read_prop:
        configs.load(read_prop)
    return configs