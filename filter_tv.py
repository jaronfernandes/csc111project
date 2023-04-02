"""CSC111 Course Project: filter_tv.py

Module description
===============================

This Python module is responsible for loading the TV series dataset (which is file TV Series.csv)
It then cleans up missing entries, filteres for relevant entries in columns and renames columns
to form a final IMDB show dataset (file final_imdb_shows.json).

This file is Copyright (c) 2023 Jaron Fernandes, Ethan Fine, Carmen Chau, Jaiz Jeeson
"""
import json
import pandas as pd


def tv_show_json() -> pd.DataFrame:
    """Makes a revised dataframe based on the TV Series.csv file

       Overall outline of changes made from original TV Series.csv file

       1. Only including certain columns (Rating, Genre, Synopsis, Release Year, Series Title). Renamed these columns
        to be consistent with how other revised datasets will be named

       2. Only including IMDB TV shows whose entries in the columns we cared about (see Project Report for the specific
       columns) were not missing values (these were usually represented in the form '****')

       3. Also only keeping IMDB TV shows with ratings higher than 5.0 and those that have complete synopses

       Futher on in the function body, we had to reformat entry dates, see comments for more details
    """

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
    # df["release_date"] = df["release_date"].transform(lambda x: str(x)[1:5])

    # Need to handle dates seperately due to some dates being formatted differently
    # In particular, the II and I characters had to be handled
    for i, row in df.iterrows():
        if "II" in str(row.release_date):
            df.at[i, "release_date"] = row.release_date[6:10]
        elif "I" in str(row.release_date):
            df.at[i, "release_date"] = row.release_date[5:9]
        else:
            df.at[i, "release_date"] = str(row.release_date)[1:5]
    # After this processing, around 4-5 show entries still had dates that were misformatted
    # We have decided to remove these entries entirely from our dataset by updating our dataframe accordingly
    df = df[df.release_date != "an"]
    df = df[df.release_date != "(202"]
    df = df[df.release_date != "(201"]
    return df


def loading_json(show_dataframe: pd.DataFrame) -> None:
    """
    Write information contained in show_dataframe (that contains IMDB TV show entries)
    into the final_imdb_shows.json file

    Preconditions:
        - show_dataframe is a Panda DataFrame that is formatted according to the output from
         method tv_show.json()
    """
    # Convert dataframe to JSON object
    json_data = json.loads(show_dataframe.to_json(orient='records'))

    # Write JSON data to file
    with open('datasets/filtered/final_imdb_shows.json', 'w') as f:
        json.dump(json_data, f, indent=4)

    # IMPORTANT: PLEASE READ:
    # You can test that the filtering and loading functionalities of this file work by commenting out
    # the above "with open" commands and uncommenting the test commands below
    # You then NEED TO RUN THE MAIN BLOCK
    # This would create a new file called test_imdb_shows.json that
    # should have the same entries as final_imdb_shows.json...
    # ... and formatted in a similar way too
    # The only difference would be that ratings and release dates would be strings in the test file
    # This is because in keyword_graph_maker.py, which is where we ran our final_imdb_shows.json file,...
    # ... both attributes became integers
    # with open('datasets/filtered/test_imdb_shows.json', 'w') as f:
    #     json.dump(json_data, f, indent=4)


if __name__ == '__main__':
    # tv_show_dataframe = tv_show_json()
    # loading_json(tv_show_dataframe)

    # Enabling doctest checking features:

    import doctest

    doctest.testmod(verbose=True)

    # Enabling python_ta configurations:
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["json", "pandas"],
        'allowed-io': ["loading_json"],
        'disable': [''],
        'max-line-length': 120,
    })
