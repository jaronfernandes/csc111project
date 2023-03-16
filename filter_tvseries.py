"""another thing"""
import json
import pandas as pd


def extract_year(year: float) -> str:
    """extracts the start year of a year string from the dataframe"""
    return str(year)[1:5]


# Read the csv file and store as pandas dataframe
df = pd.read_csv('dataset/TV Series.csv')

# Manipulate dataframe
df = df[df["Rating"] != '****']
df = df[df["Synopsis"] != '****']
df = df[df["Release Year"] != '****']
df = df[df["Genre"] != '****']
df.drop(columns='Cast', inplace=True)
df.drop(columns='Runtime', inplace=True)
df["Release Year"] = df["Release Year"].apply(extract_year)
df = df.rename(columns={
    'Rating': 'rating',
    'Genre': 'genre',
    'Synopsis': 'plot_summary',
    'Release Year': 'release_date',
    'Series Title': 'title'
})

# Convert dataframe to JSON object
json_data = json.loads(df.to_json(orient='records'))

# Write JSON data to file
with open('final_shows.json', 'w') as f:
    json.dump(json_data, f, indent=4)
