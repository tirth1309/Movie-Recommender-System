import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import matplotlib.pyplot as plt

df = pd.read_csv('data/current/csv/user_data_1.csv')

# Count the number of male (M) and female (F) users
gender_counts = df['Gender'].value_counts()
print(gender_counts)
# Generate visualization for gender distribution
plt.figure(figsize=(8, 5))
plt.bar(gender_counts.index, gender_counts, color=['blue', 'pink'])
plt.title('Gender Distribution of Users')
plt.xlabel('Gender')
plt.ylabel('Number of Users')
plt.xticks(rotation=0)
plt.show()

# Generate visualization for age group distribution
age_bins = [10 * i for i in range(df['Age'].min() // 10, (df['Age'].max() // 10) + 2)]
age_group_labels = [f'{i}-{i+9}' for i in range(df['Age'].min() // 10 * 10, (df['Age'].max() // 10 + 1) * 10, 10)]
df['Age_Group'] = pd.cut(df['Age'], bins=age_bins, labels=age_group_labels)

age_group_counts = df['Age_Group'].value_counts().sort_index()
print(age_group_counts)
plt.figure(figsize=(10, 5))
plt.bar(age_group_counts.index, age_group_counts, color='skyblue')
plt.title('Age Group Distribution of Users')
plt.xlabel('Age Group')
plt.ylabel('Number of Users')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()