"""CSC111 Course Project: filter_movies.py

Module description
===============================

This Python module is responsible for loading the IMDB media dataset (which is file filtered_basics.txt)
and the IMDB movie details dataset (which is file IMDB_movie_details.json). It then merges the 2 datasets
together to form a final IMDB movie dataset (file final_imdb_movies.json).

This file is Copyright (c) 2023 Jaron Fernandes, Ethan Fine, Carmen Chau, Jaiz Jeeson
"""
import csv
import json


def load_json_file(filename: str) -> list[dict]:
    """Opens a json file and returns a list of its contents.

    Preconditions:
        - filename is a valid json file name

    """
    file_contents_so_far = []

    with open(filename, 'r') as file:
        for line in file:
            print(line)
            file_contents_so_far.append(json.loads(line))

    return file_contents_so_far


def load_json_file_animes(filename: str) -> list[dict]:
    """Opens a json file and returns a list of its contents.

    Preconditions:
        - filename == 'datasets/filtered/final_animes.json'
    """
    file_contents_so_far = []

    with open(filename, 'r') as file:
        string = file.read()
        for line in json.loads(string):
            print(line)
            file_contents_so_far.append(line)

    return file_contents_so_far


def get_id_to_movies(file_contents: list[dict]) -> dict:
    """Returns a dictionary mapping id to movies from the IMDb json file.
    """
    id_to_movies = {}

    for movie in file_contents:
        id_to_movies[movie['movie_id']] = movie

    return id_to_movies


def merge_datasets(json_filename: str, text_filename: str, new_filename: str) -> None:
    """
    Merges the IMDb json file (named json_filename), the IMDb txt file (named text_filename)
       to create a new json file (named new_filename).

    Preconditions:
       - json_filename refers to a file in the .json file format
       - text_filename refers to a file in the .txt file format
       - new_filename refers to a file in the .json file format
       - json_filename and text_filename follow the formats of IMDB_movie_details.json and filtered_basics.txt
       respectively
    """

    file_contents = load_json_file(json_filename)
    id_to_movies = get_id_to_movies(file_contents)

    with open(text_filename) as csv_file:
        reader = csv.reader(csv_file)
        next(reader)

        unchecked_keys = set(id_to_movies.keys())

        for row in reader:
            id_to_movies[row[0]]['release_date'] = id_to_movies[row[0]]['release_date'][0:4]

            if row[0][0:2] == 'tt' and row[1] == 'movie' and row[0] in id_to_movies:
                # The above if statement checks if the ID of the current movie entry in the IMDB text dataset...
                # ... corresponds to a movie entry in the IMDB json file.
                id_to_movies[row[0]]['title'] = row[3]  # Title of movie changed to the name on the IMDB text file
                unchecked_keys.remove(row[0])
                id_to_movies[row[0]].pop('plot_synopsis')
                id_to_movies[row[0]].pop('duration')

        for key in unchecked_keys:
            id_to_movies.pop(key)

        with open(new_filename, 'w') as new_file:  # Converting the new dictionary of movies into a JSON file, then
            # storing it
            json.dump(list(id_to_movies.values()), new_file, indent=4)


if __name__ == '__main__':
    merge_datasets('datasets/raw/IMDB_movie_details.json', 'datasets/raw/filtered_basics.txt',
                   'datasets/filtered/test_imdb_movies.json')

    # IMPORTANT: PLEASE READ:
    # You can test that the filtering and loading functionalities of this file work by commenting out
    # the above "merge_datasets" call and instead include the following call below
    # merge_datasets('datasets/raw/IMDB_movie_details.json', 'datasets/raw/filtered_basics.txt',
    #                'datasets/filtered/test_imdb_movies.json')
    # This would create a new file called test_imdb_movies.json that
    # should have the same entries as final_imdb_shows.json...
    # ... and formatted in a similar way too
    # The only difference would be that ratings and release dates would be strings in the test file
    # This is because in keyword_graph_maker.py, which is where we ran our final_imdb_movies.json file,...
    # ... both attributes became integers

    # Enabling doctest checking features:

    import doctest

    doctest.testmod(verbose=True)

    # Enabling python_ta configurations:
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["json", "csv"],
        'allowed-io': ["load_json_file", "get_id_to_movies", "merge_datasets", "load_json_file_animes"],
        'max-line-length': 120,
    })
