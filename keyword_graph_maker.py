"""creates the keyword graph by getting keywords from all the synposes in final_shows and final_movies
"""
import pandas as pd
import json
import random
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import spacy


# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')


def word_similarity(word1: str, word2: str) -> float:
    """Uses spacy's en_core_web_lg module to compute semantic similarity between two words. Outputs a float between 0
    and 1.
    """
    token1 = nlp(word1)
    token2 = nlp(word2)
    return token1.similarity(token2)


def get_anime_keywords(anime_file: str) -> set[str]:
    """Gets genres from filtered anime file as keywords.
    """
    tvshows = pd.read_json(anime_file)
    words = set()
    for index, _ in tvshows.iterrows():
        words_to_add = tvshows.at[index, 'keywords']
        words.update(set(words_to_add))
    return words


def get_imdb_keywords(imdb_file: str, column: str) -> set[str]:
    """Makes a set of all keywords from synopses of IMDb movies or IMDb shows (stored in imdb_file).

    Preconditions:
        - column must be a valid column in imdb_file.
    """
    with open(imdb_file) as f:
        data = json.load(f)

    keyword_set = set()  # start off with the keywords from the final anime entries keywords
    for entry in data:
        synopsis = entry[column]
        words = nltk.word_tokenize(synopsis)  # tokenize string
        nouns = set()  # empty set to hold all nouns
        word_types = nltk.pos_tag(words)
        for word, pos in word_types:
            if len(word) > 2 and (pos == 'NN' or pos == 'NNS'):
                word = wnl.lemmatize(word, pos='n')
                nouns.add(word.lower())
        keyword_set.update(nouns)
    return keyword_set


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


def make_edges(keyword_file: str, threshold: float, sampling: bool = False) -> set[tuple]:
    """Creates edges between any two keywords in keyword_file with similarity score greater than threshold. Returns a
    set of tuples, where each tuple represents an edge.
    """
    with open(keyword_file, 'r') as file:
        lines = file.readlines()

    keyword_set = set(lines[0].split("', '"))
    if sampling:
        keyword_set = random.sample(list(keyword_set), 50)
    edges = set()
    wn_lemmas = set(wn.all_lemma_names())

    for word in keyword_set:
        for other_word in keyword_set:
            if word in wn_lemmas and other_word in wn_lemmas and \
                    word != other_word and (word, other_word) not in edges:
                similarity_score = word_similarity(word, other_word)
                if similarity_score > threshold:
                    edges.add((word, other_word))
    return edges


def write_keywords(keyword_file: str) -> None:
    """Writes a set of all keywords into keyword_file in the .txt format.
    """
    keyword_set = extract_all_keywords('datasets/filtered/final_imdb_movies.json',
                                       'datasets/filtered/final_imdb_movies.json',
                                       'datasets/filtered/final_animes.json',
                                       'plot_summary')

    with open(keyword_file, 'w') as f:
        f.write(str(keyword_set))


def write_edges(edge_file: str) -> None:
    """Writes a set of all edges into edge_file in the .txt format.
    """
    connections = make_edges('datasets/filtered/keyword_graph.txt', 0.6)
    with open(edge_file, 'a') as f:
        f.write('\n' + str(connections))


if __name__ == '__main__':
    # makes sure this is only run after all the filtered datasets are finalized
    wnl = WordNetLemmatizer()
    nlp = spacy.load('en_core_web_lg')

    # IMPORTANT!!! (read the following comment):
    # comment this next line if the datasets/filtered/keyword_graph.txt file already exists with 1 line, to save time:
    write_keywords('datasets/filtered/keyword_graph.txt')  # this will create a keyword_graph.txt file

    # only run this if the previous line has been run or the txt file already exists with a valid keywords set in line 1
    # write_edges('datasets/filtered/keyword_graph.txt')  # this will read that keyword_graph.txt file and then write a
    # second line onto it
