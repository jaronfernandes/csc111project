"""thing"""
import json
import pandas as pd


def get_genres() -> set[str]:
    """looks through the imdb_shows.json for all the different genres names"""
    tvshows = pd.read_json('datasets/filtered/final_imdb_shows.json')
    genres = set()
    for index, row in tvshows.iterrows():
        genres_to_add = tvshows.at[index, 'genre'].split(', ')
        genres.update(set(genres_to_add))
    return genres


def anime_based_json() -> pd.DataFrame:
    """makes a dataframe based on the Anime.csv file"""
    new_anime = pd.read_csv('datasets/raw/Anime.csv')
    bad_strings = {
        'II', ' - ', ': ', 'Season', 'season', 'part', 'arc', 'Re-',
        '!! ', '2nd', ' 2', ' 3', ' 4', ' 5', ' 6', ' 7', 'II', 'III'
    }
    exceptions = {'1st'}
    new_anime = new_anime[["Name", "Japanese_name", "Tags", "Release_year", "Rating", "Description", "Type"]]
    new_anime = new_anime[new_anime['Type'].apply(lambda form: 'TV' in form)]
    new_anime = new_anime[new_anime['Rating'].apply(lambda score: float(score) >= 3.7)]
    new_anime = new_anime[new_anime['Release_year'].apply(lambda year: isinstance(year, float))]
    new_anime = new_anime[new_anime['Name'].apply(
        lambda title: not any(x in title for x in bad_strings) or any(x in title for x in exceptions)
    )]
    new_anime['Rating'] = new_anime['Rating'].transform(lambda x: str(x*2))
    new_anime['Release_year'] = new_anime['Release_year'].transform(lambda x: str(x))
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


def tv_show_cleaning() -> pd.DataFrame:
    """This function isn't the one we'll be using to get the anime final json"""
    new_anime = pd.read_csv('datasets/raw/Anime.csv')
    tvshows = pd.read_json('datasets/filtered/final_imdb_shows.json')
    tvshows = tvshows[tvshows['genre'].apply(lambda genres: 'Animation' in genres)]
    tvshows = tvshows[tvshows['rating'].apply(lambda score: float(score) >= 5.0)]
    tvshows = tvshows.assign(tags='')
    new_tvshows = tvshows.copy()

    for index, row in tvshows.iterrows():
        show_name = str(tvshows.at[index, 'title'])
        for i in range(0, len(show_name)):
            correction = {'î': 'i', 'ô': 'o', '×': ' x ', 'û': 'u'}
            if show_name[i] in correction:
                show_name = show_name[0:i] + correction[show_name[i]] + show_name[i+1:len(show_name)]
        found_match = False
        for index_a, row_a in new_anime.iterrows():
            anime_name = str(new_anime.at[index_a, 'Name'])
            anime_japanese_name = str(new_anime.at[index_a, 'Name'])
            if ((not isinstance(tvshows.at[index, 'release_date'], float) or not
                    isinstance(new_anime.at[index, 'Release_year'], float)) or
                    int(tvshows.at[index, 'release_date']) == int(new_anime.at[index_a, 'Release_year'])) and \
                    (show_name.lower() in anime_name.lower() or show_name.lower() in anime_japanese_name.lower()):
                if new_tvshows.at[index, 'tags'] == '':
                    new_tvshows.at[index, 'tags'] = set(new_anime.at[index_a, 'Tags'].split(', '))
                else:
                    new_tvshows.at[index, 'tags'].update(set(new_anime.at[index_a, 'Tags'].split(', ')))
                found_match = True
        if not found_match:
            print('dropped ' + str(show_name))
            new_tvshows.drop(index, inplace=True)
        else:
            print('added ' + str(show_name))
    return new_tvshows


def write_file(df: pd.DataFrame) -> None:
    """write the final_animes.json file"""
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
                    # entry['keywords'].remove('Sci Fi')
                # else:
                #     entry['keywords'].remove(word)
                if entry['genre'] == '':
                    entry['genre'] = [word]
                else:
                    entry['genre'].append(word)

            elif 'Based on' in word:
                entry['keywords'].remove(word)

    # Write JSON data to file
    with open('datasets/filtered/final_animes.json', 'w') as f:
        json.dump(json_data, f, indent=4)


if __name__ == '__main__':
    write_file(anime_based_json())
