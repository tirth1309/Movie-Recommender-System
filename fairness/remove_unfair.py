import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Assume df is your existing DataFrame with the combined data.
# Assuming user_data_df is the DataFrame created from user_data.csv.
def remove_unfair_train_data():
    df = pd.read_csv('data/current/csv/merged_users_movies.csv')
    # Create a dictionary for rows where the age is less than 21 and adult is True.
    age_adult_dict = {
        row['User_ID']: row['Movie_Ids']
        for _, row in df[(df['Age'] < 21) & (df['adult'] == True)].iterrows()
    }
    print(age_adult_dict)
    # Remove those entries from the other CSV.
    user_data_df = pd.read_csv('data/current/csv/user_data_1.csv')
    user_data_df['User_ID'] = user_data_df['User_ID'].astype('Int64')
    user_data_df['Movie_Duration'] = user_data_df['Movie_Duration'].astype('Int64')
    # Filter the user_data_df DataFrame to remove entries that match the User_ID and Movie_Ids in the dictionary.
    user_data_df = user_data_df[~user_data_df.apply(lambda row: age_adult_dict.get(row['User_ID']) == row['Movie_Ids'], axis=1)]

    # Save the filtered DataFrame to a new CSV file.
    user_data_df.to_csv('data/current/csv/user_data_1.csv', index=False)

user_id = 272025
recommendation = ['the+400+blows+1959', 'the+godfather+1972', 'central+station+1998', 
                  'the+shawshank+redemption+1994', 'buena+vista+social+club+1999', 'm+1931', 
                  'my+neighbor+totoro+1988', 'the+princess+and+the+warrior+2000', 'once+2007', 
                  'castle+in+the+sky+1986',' bob+roberts+1992', 'schindlers+list+1993', 
                  'witness+for+the+prosecution+1957', 'paths+of+glory+1957', 
                  'in+the+mood+for+love+2000', 'harold+and+maude+1971', 'the+seventh+seal+1957', 
                  'princess+mononoke+1997', 'little+big+man+1970', 'his+girl+friday+1940', 
                  'the+apartment+1960', 'no+mans+land+2001', 'rashomon+1950', 
                  'the+triplets+of+belleville+2003', 'erotic+nights+of+the+living+dead+1980']

def remove_unfair_recommendation_pred(user_id, recommendation):
    print('Removing unfair prediction')
    movies_df = pd.read_csv('data/current/csv/movies_m1.csv')

    # Read the user dataset
    users_df = pd.read_csv('data/current/csv/user_data_1.csv')
    user_age = users_df.loc[users_df['User_ID'] == user_id, 'Age'].values[0]

    # Replace adult movies in recommendation if user is under 21
    if user_age < 21:
        # Filter movies_df to get only adult movies
        adult_movies = set(movies_df[movies_df['adult'] == True]['id'].tolist())
        
        # Update the recommendation list
        updated_recommendation = ['harry+potter+and+the+deathly+hallows+part+2+2011' if movie in adult_movies else movie for movie in recommendation]
    else:
        updated_recommendation = recommendation

    print(updated_recommendation)

#remove_unfair_train_data()
remove_unfair_recommendation_pred(user_id,recommendation)

