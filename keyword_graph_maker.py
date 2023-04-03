"""CSC111 Course Project: keyword_graph_maker.py

Module description
===============================

This Python module is responsible for creating a text file (called keyword_graph.txt)
that contains 2 key pieces of information pertaining to the keyword graph. Firstly, it write a set of all keywords
from all the synposes in final_animes.json, final_imdb_movies.json, and final_imdb_shows.json.
Then, in the same text file, it also writes a set of edges between all keywords in the generated
set that have a similarity score greater than a certain threshold.

This file is Copyright (c) 2023 Jaron Fernandes, Ethan Fine, Carmen Chau, Jaiz Jeeson
"""
import json

import pandas as pd

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn, stopwords

import spacy
from spacy import tokens

# import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# Uncomment the block of code below to donwload specific nltk dependencies. Uncomment the block of code above if the
# block below raise any errors.

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('stopwords')

# Global variable that contains a list of common "stopwords" from NLKT. Stopwords are common words like "the", "an"...
# ... that provide little context to texts that are often analyzed. For our keyword graph, we will not be considering
# ... these stop words as "keywords".
STOP_WORDS = set(stopwords.words('english'))


def word_similarity(token1: tokens.doc.Doc, token2: tokens.doc.Doc) -> float:
    """Uses spacy's en_core_web_lg module to compute semantic similarity between two words. Outputs a float between 0
    and 1.
    """
    return token1.similarity(token2)


def get_anime_keywords(anime_file: str) -> set[str]:
    """Gets genres from filtered anime file (eg: final_animes.json). These will be the keywords for the anime file.

    Preconditions:
        - anime_file is a correct filename referring to a json file containing anime entries
    """
    tvshows = pd.read_json(anime_file)
    words = set()
    for index, _ in tvshows.iterrows():
        words_to_add = tvshows.at[index, 'keywords']
        words.update(set(words_to_add))
    return {x.lower() for x in words}


def get_imdb_keywords(imdb_file: str, column: str) -> set[str]:
    """Makes a set of all keywords from synopses of IMDb movies or IMDb shows. In our project, these would be
    files final_imdb_shows.json and final_imdb_movies.json

    Preconditions:
        - column must be a valid column in imdb_file.
    """
    with open(imdb_file) as f:
        data = json.load(f)

    keywords = {}
    for entry in data:
        synopsis = entry[column]

        # Get a list of tokenized words.
        words = nltk.word_tokenize(synopsis)
        nouns = set()
        word_types = nltk.pos_tag(words)
        for word, pos in word_types:

            # Get only words that are nouns and non-stop words.
            if (pos in {'NN', 'NNS'}) and word not in STOP_WORDS:
                word = wnl.lemmatize(word, pos='n')  # Ensure that lemmatization occurs for a noun to avoid ambiguity.

                # Ensure that words are long enough and are not hyperlinks.
                if len(word) >= 3 and '.' not in word:
                    nouns.add(word.lower())
        for word in nouns:
            if word in keywords:
                keywords[word] += 1
            else:
                keywords[word] = 1
    return set(x for x in keywords if keywords[x] > 1)


def extract_all_keywords(movie_file: str, show_file: str, anime_file: str, column: str) -> set[str]:
    """Creates a set of all keywords from show_file, movie_file and anime_file.

    Preconditions:
        - column must be a valid column in movie_file and show_file.
    """
    anime_keywords = get_anime_keywords(anime_file)
    show_keywords = get_imdb_keywords(show_file, column)
    movie_keywords = get_imdb_keywords(movie_file, column)
    keywords = {*anime_keywords, *movie_keywords, *show_keywords}
    return keywords


def get_keywords_from_file(keyword_file: str) -> tuple[list[tokens.doc.Doc] | set, int]:
    """Read and return TOKENIZED contents of keyword_file with number of keywords.
    We need to tokenize (a process in NLKT that refers to parsing text and characters)
    in order to be able to compare keyword similarity in method make_edges.

    Preconditions:
        - keyword_file is a name of a txt file that contains a set of keywords
    """
    with open(keyword_file, 'r', encoding='LATIN-1') as file:
        lines = file.readlines()

    # Convert first line of keyword file (keyword vertices) into a Python list of keyword vertices.
    keyword_set = lines[0].split("', '")
    keyword_set[0] = keyword_set[0].strip("{'")
    keyword_set[-1] = keyword_set[-1].strip("'}")

    length = len(keyword_set)

    # Return tokenized keywords (using spacy's en-core-web-lg' language model) and the number of keywords.
    return [nlp(keyword) for keyword in keyword_set], length


def make_edges(keyword_token_list: list[tokens.doc.Doc], length: int, threshold: float, start_chunk: int = 0,
               end_chunk: int = 0) -> set[tuple]:
    """Creates edges between any two keywords in keyword_file with similarity score greater than threshold. Returns a
    set of tuples, where each tuple represents an edge.

    List of arguments:
    - keyword_token_list: Is a list of tokenized keywords
    - length: The length of the keyword_set
    - threshold: For 2 keywords to form an edge, their similarity score (between 0 and 1 inclusive) must be > threshold
    - start_chunk: The index of the keyword token list we are starting to make edges from
    - end_chunk: The index of the keyword token list we are ending on
    - sampling: Argument to determine whether we are sampling from a random subset of keyword_token_list

    Preconditions:
        - threshold >= 0.0 and threshold <= 1.0
        - end_chunk <= the length of the keyword file
    """
    edges = set()

    # Get set of all lemmas.
    wn_lemmas = set(wn.all_lemma_names())

    for i in range(start_chunk, end_chunk):
        word = str(keyword_token_list[i])
        for j in range(length):
            other_word = str(keyword_token_list[j])

            # Only pairs of words that are in their lemmatized form and do not already share an edge.
            if word in wn_lemmas and other_word in wn_lemmas and \
                    word != other_word and (word, other_word) not in edges and \
                    (other_word, word) not in edges:

                similarity_score = word_similarity(keyword_token_list[i], keyword_token_list[j])

                # Create edge if the similarity score is above a custom threshold.
                if similarity_score > threshold:
                    edges.add((word, other_word))
    return edges


def write_keywords(keyword_file: str) -> None:
    """Writes a set of all keywords into keyword_file in the .txt format.
    """
    keyword_set = extract_all_keywords('datasets/filtered/final_imdb_movies.json',
                                       'datasets/filtered/final_imdb_shows.json',
                                       'datasets/filtered/final_animes.json',
                                       'plot_summary')

    with open(keyword_file, 'w') as f:
        f.write(str(keyword_set))


def write_edges(edge_file: str, tokenized_list: list, length: int, threshold: float,
                bound: tuple[int, int]) -> None:
    """Writes a set of all edges into edge_file in the .txt format.
    """
    start, end = bound

    connections = make_edges(tokenized_list, length, threshold, start_chunk=start, end_chunk=end)
    with open(edge_file, 'a') as f:
        f.write('\n' + str(connections))


def update_dataset_keywords(reference_file: str, edit_file: str, column: str) -> None:
    """Only to be run after the keyword_graph.txt file has at least the first line completed
    i.e. write_keywords() has been called. Updates IMDb movie and TV show databases with keywords found.

    Preconditions
    - the column is a valid column of the edit_file's json dataframe, and contains a string
    """
    df = pd.read_json(edit_file)
    # df = df.loc[:, ~df.columns.isin(['plot_synopsis', 'duration'])]
    df = df.assign(keywords='')
    with open(reference_file, 'r', encoding='LATIN-1') as file:
        lines = file.readlines()

    keywords = set(lines[0].split("', '"))

    for index, _ in df.iterrows():
        synopsis = df.at[index, column].split(' ')
        for phrase in keywords:
            if phrase in synopsis:

                # Assign a list consisting of keywords to the movie if no such list already exists. Else, append to...
                # ...existing list.
                if df.at[index, 'keywords'] == '':
                    df.at[index, 'keywords'] = [phrase]
                else:
                    df.at[index, 'keywords'].append(phrase)

    # Read and write data into edit_file by converting the dataframe to the .json format.
    json_data = json.loads(df.to_json(orient='records'))
    with open(edit_file, 'w') as f:
        json.dump(json_data, f, indent=4)


if __name__ == '__main__':
    wnl = WordNetLemmatizer()
    nlp = spacy.load('en_core_web_lg')

    # Creates and stores keyword vertices in keyword_graph.txt.
    # write_keywords('datasets/filtered/keyword_graph.txt')

    # Run the block of code below after keyword vertices have been created. These update the movie and TV show...
    # ...datasets to store keywords with the appropriate shows.
    # update_dataset_keywords('datasets/filtered/keyword_graph.txt',
    #                         'datasets/filtered/final_imdb_movies.json', 'plot_summary')
    # update_dataset_keywords('datasets/filtered/keyword_graph.txt',
    #                         'datasets/filtered/final_imdb_shows.json', 'plot_summary')

    # Run the line of code below to extract keywords and return them tokenized.
    # keyword_set, num_keywords = get_keywords_from_file('datasets/filtered/keyword_graph.txt')

    # Run this line next. Creates and stores keyword edges in keyword_graph.txt.
    # write_edges('datasets/filtered/keyword_graph.txt', keyword_set, num_keywords, 0.65, (0, num_keywords))

    # Enable python_ta configurations:
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["pandas", "json", "nltk", "spacy", "nltk.stem", "nltk.corpus"],
        'allowed-io': ["get_imdb_keywords", "get_keywords_from_file", "write_keywords", "write_edges",
                       "write_dataset_keywords", "update_dataset_keywords"],
        'disable': ['E1101', 'F0002'],
        'max-nested-blocks': 4,
        'max-line-length': 120,
    })
