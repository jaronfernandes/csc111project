"""thing"""
import json
import pandas as pd

new_anime = pd.read_csv('dataset/Anime.csv')
# anime2 = pd.read_csv('dataset/animes.csv')   this dataset will not be used for this
tvshows = pd.read_json('dataset/final_shows.json')

new_anime = new_anime[["Name", "Tags", "Rating"]]

unique_titles = set(new_anime['Name'])

# Apply the function to each row in the genres column and filter the dataframe
tvshows = tvshows[tvshows['genre'].apply(lambda genres: 'Animation' in genres)]

# Filter new_anime to only have entries with titles in unique_titles
tvshows_only_animes = tvshows[tvshows['title'].isin(unique_titles)]
tvshows_only_animes = tvshows_only_animes.assign(tags='')

# Group new_anime by title and aggregate the tags into a set for each title
anime_tags = new_anime.groupby('Name')['Tags'].apply(set)


# Define a function to get the tags for a given title from tags_by_title
def get_tags(title: str) -> set:
    """gets the tags for a title entry
    """
    if title in anime_tags:
        return anime_tags[title]
    else:
        return set()


# Apply the function to each row in filtered_df_A and add a tags column
tvshows_only_animes['tags'] = tvshows_only_animes['title'].apply(get_tags)

# Convert dataframe to JSON object
json_data = json.loads(tvshows_only_animes.to_json(orient='records'))

for entry in json_data:
    tags = entry['tags']
    entry['tags'] = list(tags[0].split(','))

# Write JSON data to file
with open('final_animes.json', 'w') as f:
    json.dump(json_data, f, indent=4)
