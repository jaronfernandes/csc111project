"""thing"""
import json
import pandas as pd
import math

new_anime = pd.read_csv('datasets/raw/Anime.csv')
# anime2 = pd.read_csv('dataset/animes.csv')   this dataset will not be used for this
tvshows = pd.read_json('datasets/filtered/final_imdb_shows.json')

new_anime = new_anime[["Name", "Japanese_name", "Tags"]]

unique_titles = set(new_anime['Name'])
unique_japanese_titles = set(new_anime['Japanese_name'])
new_unique_japanese_titles = unique_japanese_titles.copy()
for n in unique_japanese_titles:
    if not isinstance(n, str) and math.isnan(n):
        new_unique_japanese_titles.remove(n)

# Apply the function to each row in the genres column and filter the dataframe
tvshows = tvshows[tvshows['genre'].apply(lambda genres: 'Animation' in genres)]


def shares_3_words_in_order(str1, str2):
    """used to see if titles are similar enough"""
    # split the strings into lists of words
    words1 = str1.split()
    words2 = str2.split()
    if len(words1) < 3:
        goal = len(words1)
    else:
        goal = 3
    count = 0
    i = 0
    for j in range(len(words2)):
        if words1[i] == words2[j]:
            count += 1
            i += 1
        if count >= goal:
            return True
        if i >= len(words1):
            break

    return False


new_tvshows = tvshows.copy()
# Filter new_anime to only have entries with titles in unique_titles
for index, row in tvshows.iterrows():
    show = str(tvshows.at[index, 'title'])
    for i in range(0, len(show)):
        correction = {'î': 'i', 'ô': 'o', '×': ' x '}
        if show[i] in correction:
            show = show[0:i] + correction[show[i]] + show[i+1:len(show)]
    if not any((show.lower() in x.lower()) for x in unique_titles) and \
            not any((show.lower() in x.lower()) for x in new_unique_japanese_titles):
        new_tvshows.drop(index, inplace=True)

new_tvshows = new_tvshows.assign(tags='')

# Group new_anime by title and aggregate the tags into a set for each title
anime_tags = new_anime.groupby('Name')['Tags'].apply(set)
anime_tags2 = new_anime.groupby('Japanese_name')['Tags'].apply(set)


# Define a function to get the tags for a given title from tags_by_title
def get_tags(title: str) -> set:
    """gets the tags for a title entry
    """
    if title in anime_tags:
        return anime_tags[title]
    elif title in anime_tags2:
        return anime_tags2[title]
    else:
        return set()


# Apply the function to each row in filtered_df_A and add a tags column
new_tvshows['tags'] = new_tvshows['title'].apply(get_tags)

# Convert dataframe to JSON object
json_data = json.loads(new_tvshows.to_json(orient='records'))

for entry in json_data:
    tags = entry['tags']
    if len(tags) > 0:
        entry['tags'] = list(tags[0].split(','))

# Write JSON data to file
with open('datasets/filtered/final_animes.json', 'w') as f:
    json.dump(json_data, f, indent=4)
