"""Filtering and merging IMDb datasets."""
import json
from json import JSONDecodeError


def load_json_file(filename: str) -> list:
    """Opens a json file and returns a list of its contents."""
    file_contents_so_far = []

    with open(filename, 'r') as file:
        for line in file:
            file_contents_so_far.append(json.loads(line))

    return file_contents_so_far


def get_id_to_movies(file_contents: list) -> dict:
    """Returns a dictionary mapping id to movies from the IMDb json file."""
    id_to_movies = {}

    for movie in file_contents:
        id_to_movies[movie['movie_id']] = movie

    return id_to_movies


def merge_datasets(json_filename: str, txt_filename: str, new_filename: str) -> None:
    """Merges the IMDb json file, json_filename, and the IMDb txt file, filename2, to create a new json file with name
    new_filename.

    Preconditions:
    - json_filename refers to a file in the .json file format
    - txt_filename refers to a file in the .txt file format
    - new_filename refers to a file in the .json file format
    - json_filename and txt_filename follow the formats of imdb_1.json and imdb_2.txt respectively
    """

    file_contents = load_json_file(json_filename)
    id_to_movies = get_id_to_movies(file_contents)

    with open(txt_filename) as txt_file:
        for row in txt_file:
            if row[0][0:2] == 'tt' and row[1] == 'movie' and row[0] in id_to_movies:
                id_to_movies[row[0]]['title'] = row[3]
                id_to_movies[row[0]].pop('plot_summary')
                id_to_movies[row[0]].pop('duration')

            elif row[0][0:2] == 'tt' and row[0] in id_to_movies:
                id_to_movies.pop(row[0])

        with open(new_filename, 'w') as new_file:
            json.dump(list(id_to_movies.values()), new_file, indent=4)


merge_datasets('datasets/raw/IMDB_movie_details.json', 'datasets/raw/filtered_basics.txt',
               'datasets/filtered/final_imdb_movies.json')
