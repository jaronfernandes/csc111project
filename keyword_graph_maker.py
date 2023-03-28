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


def get_extra_keywords() -> set[str]:
    """looks through the final_animes.json for all the different genres names"""
    tvshows = pd.read_json('datasets/filtered/final_animes.json')
    words = set()
    for index, row in tvshows.iterrows():
        words_to_add = tvshows.at[index, 'keywords']
        words.update(set(words_to_add))
    return words


def word_similarity(word1: str, word2: str) -> float:
    """uses spacy's en_core_web_lg module to get the semantic similarity precentage between two words"""
    token1 = nlp(word1)
    token2 = nlp(word2)
    return token1.similarity(token2)


def make_keywords(file_name: str, column: str) -> set[str]:
    """makes a set of all the keywords
    column must be a valid column in the file_name json file
    """
    with open(file_name) as f:
        data = json.load(f)

    keyword_set = get_extra_keywords()  # start off with the keywords from the final anime entries keywords
    for entry in data:
        synopsis = entry[column]
        words = nltk.word_tokenize(synopsis)  # tokenize string
        nouns = set()  # empty set to hold all nouns
        word_types = nltk.pos_tag(words)
        for word, pos in word_types:
            if len(word) > 2 and (pos == 'NN' or pos == 'NNS'):
                word = wnl.lemmatize(word)
                nouns.add(word.lower())
        keyword_set.update(nouns)
    return keyword_set


def make_edges(file_name: str, sampling: bool = False) -> set[tuple]:
    """make edges by getting connections"""
    with open(file_name, 'r') as file:
        lines = file.readlines()

    keyword_set = set(lines[0].split("', '"))
    if sampling:
        keyword_set = random.sample(list(keyword_set), 50)
    edges = set()
    wn_lemmas = set(wn.all_lemma_names())

    for word in keyword_set:
        for other_word in keyword_set:
            if word in wn_lemmas and other_word in wn_lemmas and \
                    word != other_word and frozenset({word, other_word}) not in edges:
                similarity_score = word_similarity(word, other_word)
                if similarity_score > 0.6:
                    edges.add(tuple([word, other_word]))
    return edges


def write_vertices() -> None:
    """run this once all the filtered json files are finalized"""
    keywords = make_keywords('datasets/filtered/final_imdb_shows.json', 'plot_summary')
    with open('datasets/filtered/keyword_graph.txt', 'w') as f:
        f.write(str(keywords))


def write_edges() -> None:
    """This must be run after the previous function has been run"""
    connections = make_edges('datasets/filtered/keyword_graph.txt')
    with open('datasets/filtered/keyword_graph.txt', 'a') as f:
        f.write('\n' + str(connections))


if __name__ == '__main__':
    # makes sure this is only run after all the filtered datasets are finalized
    wnl = WordNetLemmatizer()
    nlp = spacy.load('en_core_web_lg')

    # IMPORTANT!!! (read the following comment):
    # comment this next line if the datasets/filtered/keyword_graph.txt file already exists with 1 line, to save time:
    write_vertices()  # this will create a keyword_graph.txt file

    # only run this if the previous line has been run or the txt file already exists with a valid keywords set in line 1
    write_edges()  # this will read that keyword_graph.txt file and then write a second line onto it
