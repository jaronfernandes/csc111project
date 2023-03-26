"""creates the keyword graph by getting keywords from all the synposes in final_shows and final_movies
"""
import json
import random
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('wordnet_ic')

wnl = WordNetLemmatizer()
def make_keywords():
    keyword_set = set()
    with open('datasets/filtered/final_imdb_shows.json') as f:
        data = json.load(f)

    for entry in data:
        synopsis = entry['plot_summary']

        words = nltk.word_tokenize(synopsis)  # tokenize string

        nouns = set()  # empty to lists to hold all nouns

        word_types = nltk.pos_tag(words)
        for word, pos in word_types:
            if len(word) > 2 and (pos == 'NN' or pos == 'NNS'):
                word = wnl.lemmatize(word)
                nouns.add(word.lower())
        keyword_set.update(nouns)

    with open('datasets/filtered/keyword_graph.txt', 'w') as file:
        file.write(str(keyword_set))

    return keyword_set

def make_edges():
    with open('datasets/filtered/keyword_graph.txt', 'r') as file:
        lines = file.readlines()

    keyword_set = set(lines[0].split("', '"))
    edges = set()
    # wn_lemmas = set(wn.all_lemma_names())

    sample_set = random.sample(list(keyword_set), 20)

    for word in sample_set:
        for other_word in sample_set:
            if word != other_word and frozenset({word, other_word}) not in edges:
                # if word in wn_lemmas and other_word in wn_lemmas:
                #     syns = wn.synsets(word)
                #     syns2 = wn.synsets(other_word)
                #
                #     if syns and syns2:
                #         sim = syns[0].path_similarity(syns2[0])
                #         print(sim)
                #         if sim > 0.2:
                #             edges.add(frozenset({word, other_word}))
                similarity_score = word_similarity(word, other_word)
                if similarity_score > 0.5:
                    edges.add(frozenset({word, other_word}))

    return edges


import spacy

# Load a pre-trained spaCy model
nlp = spacy.load('en_core_web_lg')

# Compute semantic similarity between two words
def word_similarity(word1, word2):
    token1 = nlp(word1)
    token2 = nlp(word2)
    return token1.similarity(token2)
#
# # Example usage
# similarity_score = word_similarity('cat', 'dog')
# print(similarity_score)
