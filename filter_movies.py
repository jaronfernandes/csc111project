"""CSC111 Course Project: filter_movies.py

Module description
===============================

This Python module is responsible for loading the IMDB media dataset (which is file filtered_basics.txt)
and the IMDB movie details dataset (which is file IMDB_movie_details.json). It then merges the 2 datasets
together to form a final IMDB movie dataset (file final_imdb_movies.json)

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2023 Jaron Fernandes, Ethan Fine, Carmen Chau, Jaiz Jeeson.
"""

import json


# from json import JSONDecodeError


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
    """Merges the IMDb json file (named json_filename), the IMDb txt file (named txt_filename)
    to create a new json file with name new_filename.

    Preconditions:
    - json_filename refers to a file in the .json file format
    - txt_filename refers to a file in the .txt file format
    - new_filename refers to a file in the .json file format
    - json_filename and txt_filename follow the formats of IMDB_movie_details.json and filtered_basics.txt respectively
    """

    file_contents = load_json_file(json_filename)
    id_to_movies = get_id_to_movies(file_contents)

    with open(txt_filename) as txt_file:
        for row in txt_file:
            if row[0][0:2] == 'tt' and row[1] == 'movie' and row[0] in id_to_movies:
                # The above if statement checks if the ID of the current movie entry in the IMDB text dataset...
                # ... corresponds to a movie entry in the IMDB json file
                id_to_movies[row[0]]['title'] = row[3]  # Title of movie changed to the name on the IMDB text file
                id_to_movies[row[0]].pop('plot_summary')
                id_to_movies[row[0]].pop('duration')

            elif row[0][0:2] == 'tt' and row[0] in id_to_movies:
                # If a movie is not in both the text and json file, remove it from the dictionary id_to_movies
                id_to_movies.pop(row[0])

        with open(new_filename,
                  'w') as new_file:  # Converting the new dictionary of movies into a JSON file, then storing it
            json.dump(list(id_to_movies.values()), new_file, indent=4)


if __name__ == '__main__':
    merge_datasets('datasets/raw/IMDB_movie_details.json', 'datasets/raw/filtered_basics.txt',
                   'datasets/filtered/final_imdb_movies.json')
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["json"],
        'allowed-io': ["load_json_file", "get_id_to_movies", "merge_datasets"],
        'max-line-length': 120,
    })
