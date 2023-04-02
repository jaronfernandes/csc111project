"""CSC111 Course Project: anime_filter.py

Module description
===============================

This Python module is responsible for loading the Anime media dataset (which is file Anime.csv)
It cleans up certain column entries through filtering and renames columns to form a
final anime show dataset (file final_animes.json).

This file is Copyright (c) 2023 Jaron Fernandes, Ethan Fine, Carmen Chau, Jaiz Jeeson
"""
import json
import pandas as pd


def get_genres() -> set[str]:
    """Looks through the imdb_shows.json file to retrieve all the different genres names present in show
    entries. Returns a set of these genre words """
    tvshows = pd.read_json('datasets/filtered/final_imdb_shows.json')
    genres = set()
    for index_series_pair in tvshows.iterrows():
        genres_to_add = tvshows.at[index_series_pair[0], 'genre'].split(', ')
        genres.update(set(genres_to_add))
    return genres


def anime_based_json() -> pd.DataFrame:
    """Makes a revised dataframe based on the Anime.csv file

    Overall outline of changes made from original Anime.csv file

    1. Only including certain columns (Name, Rating, Release_year, Description, Tags). Renamed these columns
    to be consistent with how other revised datasets will be named

    2. Filtered Anime.csv to only keep Anime show entries that are the first of its kind in a certain franchise
    (see Project Report for more details). Also, these anime shows must have a rating >= 3.7

    3. Also created a new column called "genre" which will be populated with genre words of that show, which was
    retrieved by cross-referencing the shows name with final imdb show dataset.
    """
    new_anime = pd.read_csv('datasets/raw/Anime.csv')
    bad_strings = {
        'II', ' - ', ': ', 'Season', 'season', 'part', 'arc', 'Re-',
        '!! ', '2nd', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', 'III'
    }
    exceptions = {'1st'}
    new_anime = new_anime[["Name", "Japanese_name", "Tags", "Release_year", "Rating", "Description", "Type"]]
    new_anime = new_anime[new_anime['Type'].apply(lambda form: 'TV' in form)]
    new_anime = new_anime[new_anime['Rating'].apply(lambda score: float(score) >= 3.7)]
    new_anime = new_anime[new_anime['Release_year'].apply(lambda year: isinstance(year, float))]
    new_anime = new_anime[new_anime['Name'].apply(
        lambda title: not any(x in title for x in bad_strings) or any(x in title for x in exceptions)
    )]
    new_anime['Rating'] = new_anime['Rating'].transform(lambda x: str(x * 2))
    new_anime['Release_year'] = new_anime['Release_year'].astype(str)
    new_anime = new_anime[["Name", "Release_year", "Rating", "Tags", "Description"]]
    new_anime = new_anime.rename(columns={
        'Name': 'title',
        'Rating': 'rating',
        'Release_year': 'release_date',
        'Description': 'plot_summary',
        'Tags': 'keywords'
    })
    new_anime = new_anime.assign(genre='')
    return new_anime

# def tv_show_cleaning() -> pd.DataFrame:
#     """This function isn't the one we'll be using to get the anime final json"""
#     new_anime = pd.read_csv('datasets/raw/Anime.csv')
#     tvshows = pd.read_json('datasets/filtered/final_imdb_shows.json')
#     tvshows = tvshows[tvshows['genre'].apply(lambda genres: 'Animation' in genres)]
#     tvshows = tvshows[tvshows['rating'].apply(lambda score: float(score) >= 5.0)]
#     tvshows = tvshows.assign(tags='')
#     new_tvshows = tvshows.copy()
#
#     for index, row in tvshows.iterrows():
#         show_name = str(tvshows.at[index, 'title'])
#         for i in range(0, len(show_name)):
#             correction = {'î': 'i', 'ô': 'o', '×': ' x ', 'û': 'u'}
#             if show_name[i] in correction:
#                 show_name = show_name[0:i] + correction[show_name[i]] + show_name[i+1:len(show_name)]
#         found_match = False
#         for index_a, row_a in new_anime.iterrows():
#             anime_name = str(new_anime.at[index_a, 'Name'])
#             anime_japanese_name = str(new_anime.at[index_a, 'Name'])
#             if ((not isinstance(tvshows.at[index, 'release_date'], float) or not
#                     isinstance(new_anime.at[index, 'Release_year'], float)) or
#                     int(tvshows.at[index, 'release_date']) == int(new_anime.at[index_a, 'Release_year'])) and \
#                     (show_name.lower() in anime_name.lower() or show_name.lower() in anime_japanese_name.lower()):
#                 if new_tvshows.at[index, 'tags'] == '':
#                     new_tvshows.at[index, 'tags'] = set(new_anime.at[index_a, 'Tags'].split(', '))
#                 else:
#                     new_tvshows.at[index, 'tags'].update(set(new_anime.at[index_a, 'Tags'].split(', ')))
#                 found_match = True
#         if not found_match:
#             print('dropped ' + str(show_name))
#             new_tvshows.drop(index, inplace=True)
#         else:
#             print('added ' + str(show_name))
#     return new_tvshows


def write_file(df: pd.DataFrame) -> None:
    """Write information contained in dataframe with anime entries into the final_animes.json file

    Preconditions:
        - df is a Panda DataFrame that is formatted according to the output from method anime_based.json()
    """
    json_data = json.loads(df.to_json(orient='records'))
    genres = get_genres()
    for entry in json_data:
        tags = entry['keywords']
        if len(tags) > 0:
            entry['keywords'] = [x.strip() for x in list(tags.split(',')) if x != '']
        possible_tags = entry['keywords'].copy()
        for word in possible_tags:
            if word in genres or word == 'Sci Fi':
                if word == 'Sci Fi':
                    word = 'Sci-Fi'
                if entry['genre'] == '':
                    entry['genre'] = [word]
                else:
                    entry['genre'].append(word)

            elif 'Based on' in word:
                entry['keywords'].remove(word)

    # Write JSON data to file
    with open('datasets/filtered/final_animes.json', 'w') as f:
        json.dump(json_data, f, indent=4)

    # IMPORTANT: PLEASE READ:
    # You can test that the filtering and loading functionalities of this file work by commenting out
    # the above "with open" commands and uncommenting the test commands below
    #  # You then NEED TO RUN THE MAIN BLOCK
    # This would create a new file called test_animes.json that should have the same entries ad final_animes.json...
    # ... and formatted in a similar way too
    # with open('datasets/filtered/test_animes.json', 'w') as f:
    #     json.dump(json_data, f, indent=4)


if __name__ == '__main__':
    # write_file(anime_based_json())

    # Enabling doctest checking features:

    import doctest

    doctest.testmod(verbose=True)

    # Enabling python_ta configurations:
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["json", "pandas"],
        'allowed-io': ["write_file"],
        'disable': ['E1101'],
        # We had to disable E1101 as in line 20 and 21, PythonTA was confusing variable tvshows as being a Json Reder
        # ... object, when in fact, doing type(tvshows) revelas that it is a DataFrame, which has access to attributes
        # ... like "iterrows" and "at"
        'max-line-length': 120,
        'max-nested-blocks': 4
    })
