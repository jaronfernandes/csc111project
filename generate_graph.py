"""Generate graph file"""
import csv
from difflib import SequenceMatcher  # TODO/FIXME: I added as an improv for checking similarity. Read below for more.


# TODO: Here in case we need it in the future (to potentially extract from movie_details)
import json


from part0 import RecommendationGraph, _Vertex

# The higher the number, the higher chance that more duplicate anime shows will appear, from 0.0 to 1.0
TEXT_SIMILARITY_DEGREE = 0.8
# Limits to constrain the graph to a small enough size for a feasible running-time.
ANIME_DATASET_LIMIT = 20000
IMDB_DATASET_LIMIT = 10


def extract_animes(anime_file_one: str, anime_file_two: str, graph: RecommendationGraph) -> (RecommendationGraph, list):
    """extract animes"""
    # TODO/FIXME: In case we want to clean up the code and handle it in helper functions
    #  (which should probably be done...)


def extract_imdb(imdb_file_one: str, imdb_file_two: str, graph: RecommendationGraph, anime_strs: list[str]) \
        -> (RecommendationGraph, list):
    """extract movies"""
    # TODO/FIXME: In case we want to clean up the code and handle it in helper functions
    #  (which should probably be done...)


def calculate_connection(item1: str, item2: str, graph: RecommendationGraph) \
        -> tuple[float, float, float, float, float]:
    """sample calculate connection thing.


    item1 is the anime name, item2 is the IMDB name, and graph is the RecommendationGraph.

    algorithm weights:
    genres: 0.3, calculated using difflib
    rating: 0.3
    synopsis: 0.3
    year: 0.1

    Preconditions:
        - item1 and item2 are both vertices in the graph
    """
    # FIXME: This should almost definitely be improved on. Below is simply something I improvised.

    v1, v2 = graph.get_vertex(item1), graph.get_vertex(item2)
    total = 1.0

    # FIXME: Could replace .ratio() with .real_quick_ratio() whenever it is called to
    #  make it more efficient, BUT then it doesn't become as accurate (and it's worse as many
    #  will return a very large similarity rating, even if their similarity is only around 7%).
    genres = 0.3 * SequenceMatcher(None, v1.genres, v2.genres).ratio()
    total -= genres

    synopsis = 0.3 * SequenceMatcher(None, v1.synopsis, v2.synopsis).ratio()
    total -= synopsis
    year = 0.1 * SequenceMatcher(None, v1.start_end_year, v2.start_end_year).ratio()
    total -= year

    if v1.rating is not None and v2.rating is not None:
        # Multiply v1.rating by 2 because anime vertices are out of 5 while IMDB are out of 10.
        # Divide it by 10 because rating is from 0.0 to 10.0
        rating = 0.3 * abs((10 - ((v1.rating * 2) - v2.rating)) / 10)
        total -= rating
    else:
        rating = 0
        total = (total - 0.3) * (1 / 0.7)

    return (total, synopsis, genres, year, rating)


def calculate_and_set_connection(item1: str, item2: str, graph: RecommendationGraph) -> None:
    """sample calculate connection thing except it sets it as well now

    Preconditions:
        - item1 and item2 are both vertices in the graph
    """
    connections = calculate_connection(item1, item2, graph)
    graph.add_edge(item1, item2, connections)


def similarity_name_matching(name1: str, name2: str) -> float:
    """Helper function for deciding if an (anime) name is similar matching.
    """
    # FIXME: This may be improved on. Below is simply something I improvised.
    return SequenceMatcher(None, name1, name2).ratio()  # Uses SequenceMatcher from the difflib pkg for text similarity


def check_movie_in_animes(suspect: str, anime_strs: list) -> bool:
    """Helper function to check if the movie that we want to add to the graph is already an anime.

    Using the TV Series.csv file, it isn't as specific as the anime datasets with regards
    to name conventions (ex. same spelling, no "season 1", "season 2", etc.)

    Preconditions:
        - anime_vertices is a list of vertices
    """
    # FIXME: This may be improved on. Below is simply something I improvised.
    for anime_name in anime_strs:
        if suspect in anime_name or similarity_name_matching(suspect, anime_name) > TEXT_SIMILARITY_DEGREE:
            return True

    return False


def load_graph(imdb_file: str,
               anime_file_one: str,
               anime_file_two: str = None,
               filter_similar_names: bool = False
               ) -> RecommendationGraph:
    """Load graph function. In-dev.

    Sample imdb files: TV Series.csv, filtered_basics.txt, filtered_basics_small.txt, title.basics.tsv,
    Sample anime files: Anime.csv, Anime_small.csv, animes.csv

    Recommended AND supported imdb files: TV Series.csv
    Recommended AND supported anime files: Anime.csv, Anime_small.csv

    Doctests will vary depending on ANIME_DATASET_LIMIT and IMDB_DATASET_LIMIT

    IMPORTANT:
        - If filter_similar_names is True, then it will slow down immensely after 3000
        iterations of adding anime vertices. This is because of the algorithm that checks similar matching names.
        A potential fix for this would be to simply filter out similar matching names while traversing through
        the graph using Dijkstra's as implemented in part0.py, and is probably a better way to go about it.
        - Running this function on large datasets can take a while. For instance, running it on the full Anime.csv
        dataset and running it on a **LIMITED (10)** TV Series.csv dataset takes about two minutes to
        create the whole graph (both vertices and edges).
        - It's almost definitely better to keep this as an upper bound and NOT add the entire TV Series dataset.
        Instead, we should probably just check if the user's input of movies/tv shows are in the TV series file.
        From there, we take the successful matches we found (i.e. it IS in the TV series.csv dataset), and use those as
        the ONLY IMDB vertices.

    >>> test_graph = load_graph('datasets/TV Series.csv', 'datasets/Anime_small.csv')
    >>> [anime_show for anime_show in test_graph._vertices]
    ['Demon Slayer: Kimetsu no Yaiba - Entertainment District Arc', 'Fruits Basket the Final Season', 'Mo Dao Zu Shi 3',
     'Fullmetal Alchemist: Brotherhood', 'Attack on Titan 3rd Season: Part II', 'Jujutsu Kaisen', 'Attack on Titan The
     Final Season: Part II', 'Attack on Titan The Final Season', 'Demon Slayer: Kimetsu no Yaiba Movie - Mugen Train',
     'Haikyuu!! Karasuno High School vs Shiratorizawa Academy', 'your name.', 'Wednesday', 'Yellowstone',
     'The White Lotus', '1923', 'Jack Ryan', 'Tulsa King', 'Alice in Borderland', 'The Recruit', 'Willow',
     'The Last of Us']
    >>> [test_graph._vertices[vertex].neighbours for vertex in test_graph._vertices]
    ... # (too long to show)
    >>> [[(neighbour.item, test_graph._vertices[vertex].neighbours[neighbour])
    ...     for neighbour in test_graph._vertices[vertex].neighbours] for vertex in test_graph._vertices]
    ... # (too long to show)
    >>> test_graph2 = load_graph('datasets/TV Series.csv', 'datasets/Anime.csv')
    >>> [anime_show for anime_show in test_graph2._vertices]
    ... # (too long to show)
    >>> [test_graph2._vertices[vertex].neighbours for vertex in test_graph2._vertices]
    ... # (too long to show)
    """
    # FIXME: If we want to merge datasets (i.e. merging the anime and IMDB data sets, add that feature in
    #  and add another parameter to this function, possibly for the imdb dataset.

    anime_strs, imdb_strs = [], []
    graph = RecommendationGraph()

    with open(anime_file_one) as anime_one:
        reader = csv.reader(anime_one)
        next(reader)  # skip the header row

        count_anime_dataset = 1

        for row in reader:  # Assume Anime_small.csv or Anime.csv dataset.
            if count_anime_dataset > ANIME_DATASET_LIMIT:
                break

            # FIXME: Might just remove the similarity check here. Read docstring for more information.
            if row[0] == str(count_anime_dataset) and \
                    (not filter_similar_names or
                     all(similarity_name_matching(row[1], name) < TEXT_SIMILARITY_DEGREE for name in anime_strs)):

                title, genres, rating, synopsis = row[1], row[7], row[8], row[11]
                release_year = row[8]
                end_year = row[9]
                if end_year is None:
                    end_year = ''

                year = release_year + '-' + end_year

                info = [title, 'Movie', synopsis, genres, year, rating]
                graph.add_vertex(info)
                anime_strs.append(title)

            if row[0] == str(count_anime_dataset):
                count_anime_dataset += 1

    with open(imdb_file) as imdb:
        reader = csv.reader(imdb)
        next(reader)  # skip the header row

        # FIXME: If we want to merge IMDB datasets, then this part of the function will have to be edited,
        #  as well as adding a reader for the other IMDB dataset(s).

        count_imdb_dataset = 0

        for row in reader:  # Assume TV Series dataset
            if count_imdb_dataset + 1 > IMDB_DATASET_LIMIT:
                break
            if not check_movie_in_animes(row[0], anime_strs):
                title, release, genres, rating, synopsis = row[0], row[1][1:-1], row[3], row[4], row[6]
                info = [title, 'Movie', synopsis, genres, release, rating]
                graph.add_vertex(info)
                imdb_strs.append(title)

                for anime in anime_strs:
                    calculate_and_set_connection(anime, title, graph)

                count_imdb_dataset += 1

    return graph
