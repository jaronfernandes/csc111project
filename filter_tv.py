"""another thing"""
import json
import pandas as pd


# Read the csv file and store as pandas dataframe
df = pd.read_csv('datasets/raw/TV Series.csv')

# Manipulate dataframe
df = df.rename(columns={
    'Rating': 'rating',
    'Genre': 'genre',
    'Synopsis': 'plot_summary',
    'Release Year': 'release_date',
    'Series Title': 'title'
})
df = df[["rating", "genre", "plot_summary", "release_date", "title"]]
df = df.drop_duplicates()
df = df[df["release_date"].apply(lambda x: x != '****')]
df = df[df["rating"].apply(lambda x: x != '****')]
df = df[df["rating"].apply(lambda x: float(x) > 5.0)]
df = df[df["genre"].apply(lambda x: x != '****')]
df = df[df["plot_summary"].apply(lambda x: len(x) > 20)]
df["release_date"] = df["release_date"].transform(lambda x: str(x)[1:5])


# Convert dataframe to JSON object
json_data = json.loads(df.to_json(orient='records'))

# Write JSON data to file
with open('datasets/filtered/final_imdb_shows.json', 'w') as f:
    json.dump(json_data, f, indent=4)
