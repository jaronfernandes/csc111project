"""creates the keyword graph by getting keywords from all the synposes in final_shows and final_movies
"""
import pandas as pd
import json
import random
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import spacy
from spacy import tokens

# import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')
# nltk.download('stopwords')

STOP_WORDS = set(stopwords.words('english'))


### IMPORTANT ###
def word_similarity(token1: tokens.doc.Doc, token2: tokens.doc.Doc) -> float:
    """Uses spacy's en_core_web_lg module to compute semantic similarity between two words. Outputs a float between 0
    and 1.
    """
    return token1.similarity(token2)


def get_anime_keywords(anime_file: str) -> set[str]:
    """Gets genres from filtered anime file as keywords.
    """
    tvshows = pd.read_json(anime_file)
    words = set()
    for index, _ in tvshows.iterrows():
        words_to_add = tvshows.at[index, 'keywords']
        words.update(set(words_to_add))
    return {x.lower() for x in words}


def get_imdb_keywords(imdb_file: str, column: str) -> set[str]:
    """Makes a set of all keywords from synopses of IMDb movies or IMDb shows (stored in imdb_file).

    Preconditions:
        - column must be a valid column in imdb_file.
    """
    with open(imdb_file) as f:
        data = json.load(f)

    keywords = {}
    for entry in data:
        synopsis = entry[column]
        words = nltk.word_tokenize(synopsis)  # tokenize string
        nouns = set()  # empty set to hold all nouns
        word_types = nltk.pos_tag(words)
        for word, pos in word_types:
            # unique_score = sum(word_similarity(word, x) for x in words) / len(words)
            if (pos == 'NN' or pos == 'NNS') and word not in STOP_WORDS:
                word = wnl.lemmatize(word, pos='n')
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
    print('done with animes')
    show_keywords = get_imdb_keywords(show_file, column)
    print('done with shows')
    movie_keywords = get_imdb_keywords(movie_file, column)
    print('done with movies')
    keywords = {*anime_keywords, *movie_keywords, *show_keywords}
    return keywords


### IMPORTANT ###
# USE THIS ONCE TO GET LIST OF TOKENS!
def get_keywords_from_file(keyword_file: str) -> tuple[list[tokens.doc.Doc] | set, int]:
    """Read and return TOKENIZED contents of keyword_file with number of keywords."""
    with open(keyword_file, 'r', encoding='LATIN-1') as file:
        lines = file.readlines()

    # keyword_set = set(lines[0].split("', '"))

    keyword_set = lines[0].split("', '")
    keyword_set[0] = keyword_set[0].strip("{'")
    keyword_set[-1] = keyword_set[-1].strip("'}")

    length = len(keyword_set)

    return [nlp(keyword) for keyword in keyword_set], length


# IMPORTANT #
# GET KEYWORD_SET AND LENGTH FROM ABOVE FUNCTION!
def make_edges(keyword_token_list: list[tokens.doc.Doc], length: int, threshold: float, start_chunk: int = 0,
               end_chunk: int = 0) -> set[tuple]:
    """Creates edges between any two keywords in keyword_file with similarity score greater than threshold. Returns a
    set of tuples, where each tuple represents an edge.

    Arguments:
    - keyword_token_list: Is a list of tokenized keywords
    - length: The length of the keyword_set
    - threshold: For 2 keywords to form an edge, their similarity score (between 0 and 1 inclusive) must be > threshold
    - start_chunk: The index of the keyword token list we are starting to make edges from
    - end_chunk: The index of the keyword token list we are ending on
    - sampling: Argument to determine whether we are sampling from a random subset of keyword_token_list
    """
    edges = set()
    wn_lemmas = set(wn.all_lemma_names())

    for i in range(start_chunk, end_chunk):
        word = str(keyword_token_list[i])
        for j in range(length):
            other_word = str(keyword_token_list[j])
            if word in wn_lemmas and other_word in wn_lemmas and \
                    word != other_word and (word, other_word) not in edges and \
                    (other_word, word) not in edges:
                # if keyword_set[i] != keyword_set[j] and (keyword_set[i], keyword_set[j]) not in edges:
                similarity_score = word_similarity(keyword_token_list[i], keyword_token_list[j])
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


def write_edges(edge_file: str, tokenized_list: list, length: int, threshold: float, start: int, end: int) -> None:
    """Writes a set of all edges into edge_file in the .txt format.
    """
    connections = make_edges(tokenized_list, length, threshold, start_chunk=start, end_chunk=end)
    with open(edge_file, 'a') as f:
        f.write('\n' + str(connections))


def update_dataset_keywords(reference_file: str, edit_file: str, column: str) -> None:
    """Only to be run after the keyword_graph.txt file has at least the first line completed
    i.e. write_keywords() has been called.

    Preconditions
    - the column is a valid column of the edit_file's json dataframe, and it contains a string
    """
    df = pd.read_json(edit_file)
    df = df.assign(keywords='')
    with open(reference_file, 'r') as file:
        lines = file.readlines()
    keywords = set(lines[0].split("', '"))

    for index, _ in df.iterrows():
        synopsis = df.at[index, column].split(' ')
        for phrase in keywords:
            if phrase in synopsis:
                if df.at[index, 'keywords'] == '':
                    df.at[index, 'keywords'] = [phrase]
                else:
                    df.at[index, 'keywords'].append(phrase)

    json_data = json.loads(df.to_json(orient='records'))
    with open(edit_file, 'w') as f:
        json.dump(json_data, f, indent=4)


if __name__ == '__main__':
    # makes sure this is only run after all the filtered datasets are finalized
    wnl = WordNetLemmatizer()
    nlp = spacy.load('en_core_web_lg')

    # IMPORTANT!!! (read the following comment):
    # comment this next line if the datasets/filtered/keyword_graph.txt file already exists with 1 line, to save time:
    # write_keywords('datasets/filtered/keyword_graph.txt')  # this will create a keyword_graph.txt file

    # once we have all our keywords, we can update our datasets to include them
    # (we don't need to do this for final_animes since that already came with keywords (originally tags))
    # update_dataset_keywords('datasets/filtered/keyword_graph.txt',
    #                         'datasets/filtered/final_imdb_movies.json', 'plot_summary')
    # update_dataset_keywords('datasets/filtered/keyword_graph.txt',
    #                         'datasets/filtered/final_imdb_shows.json', 'plot_summary')
    #
    # # run this once
    keywords_info = get_keywords_from_file('datasets/filtered/keyword_graph.txt')
    # # only run this if the previous line has been run or the txt file already exists with a valid keywords set in line 1
    # # this will read that keyword_graph.txt file and then write a second line onto it
    write_edges('datasets/filtered/keyword_graph.txt', keywords_info[0], keywords_info[1], 0.65, 0, keywords_info[1])
