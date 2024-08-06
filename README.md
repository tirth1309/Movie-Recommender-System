Team 5 - Westworld

pip install -r requirements.txt

Data Generation

To connect to kafka and API to fetch the users and movie data, run the below

python data-generator.py

This will generate 2 json files, users.json and movies.json

Csv Generation

To generate user_data.csv from users.json run the below python file

python user-data-generator.py

To generate movies.csv from movies.json use the below ipynb file

movie_dataframe.ipynb

Model build and weights loading

To train the model and load the weights, uncomment the pkl generation lines and run below

python train.py

Flask API Run

python server.py

Note: Make sure to check the file names and file paths and update them if required or generating data at new location
