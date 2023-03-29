"""Makes sure this file is only run after 'datasets/filtered/keyword_graph.txt' is made"""
# TODO: media dataclass, compare function, other helper functions, read keywords graph function
from __future__ import annotations
import graph_classes
from typing import Optional
import json

# Commented out this code as we have yet to generate keyword edges
# with open('datasets/filtered/keyword_graph.txt', 'r') as f:
#     lines = f.readlines()
# keyword_graph = graph_classes.Graph()
# edges = eval(lines[1])
# keyword_graph.add_all_edges(edges)

# This section of the code is responsible for opening a json file and converting its contents to a dict
with open('datasets/filtered/sample_input_mix.json', 'r') as file:
    user_watch_list = json.load(file)


class Media:
    """The media class that contains metadata about a show/movie
    """
    title: str  # unique string denoting the media’s name of reference
    type: str  # is either 'movie' or 'show'
    genres: set[str]  # set of genres that apply to the media
    rating: float  # from 0 to 10 inclusive, denotes the rating score
    date: int  # the year of the media’s initial release
    synopsis: str  # string of a brief summary, contains keywords to be extracted
    keywords: set[str]  # set of words that describe the media.
    recommendation: Optional[set[tuple[set[Media], float]]]

    def __init__(self, entry: dict, form: str):
        """
        Preconditions:
        - The entry is a dictionary from a finalized json dataset that conforms with the naming scheme
        - form is either 'TV' or 'movie' or 'anime'
        """
        self.title = entry['title']
        self.type = form
        # self.genres = set(entry['genre'].split())
        self.genres = entry['genre']
        self.rating = float(entry['rating'])
        self.date = int(entry['release_date'][:4])
        self.synopsis = entry['plot_summary']
        self.keywords = set(entry['keywords'])  # Originally, entry['keywords'] was a list
        self.recommendation = set()

    def __str__(self):
        """
        Returns a string representation of a Media object
        """
        return f"Media({self.title}, {self.type}, {self.genres}, {self.rating}, {self.date}, {self.synopsis}, {self.keywords}, {self.recommendation})"

    def compare(self, other: Media, parent_set: set[Media]) -> float:
        """compares itself to another media with 4 assessments,
        and mutates its recommendation accordingly

        Preconditions:
        - other in parent_set
        """
        sim_scores = (0, 0, 0, 0)
        mul = (0.1, 0.2, 0.3, 0.4)  # this should be subject to change (and tweaking will majorly affect results)
        # 1. date comparison

        # 2. rating comparison

        # 3. genre comparison

        # 4. keyword comparison

        # balancing comparison values
        assert sum(sim_scores) <= 4  # 4 would be if it gets perfect scores in each
        assert len(sim_scores) == len(mul)
        perfect_score = 4 * sum(mul)
        return sum(sim_scores[x] * mul[x] for x in range(0, len(sim_scores))) / perfect_score

    def genre_comparison(self, other) -> float:
        """
        Compute the fraction of shared genres between itself (a Media object) and another Media object
        """
        num_genre_shared = len(self.genres.intersection(other.genres))
        return num_genre_shared / len(other.genres)

def converting_show_to_media_obj(user_input_media: list[dict]) -> list[Media]:
    """
    Takes a list of all USER INPUT MEDIA that the user has watched. For each input SHOW OR MOVIE
    , converts it into a Media object and stores it BACK to list user_input_media. Thus, this
    is a mutating method
    """
    for index in range(len(user_input_media)):
        if "movie_id" not in user_input_media[index]:  # This means that encountered entry is a SHOW
            user_input_media[index] = Media(user_input_media[index], 'show')  # Assigning attribute "type" to "show"
            user_input_media[index].genres = set(user_input_media[index].genres.split(", "))
            # In the line above, since input shows have all genres listed as 1 string, needed to split entries
        else:  # If there is a key called "movie_id" in the entry, then the entry is A MOVIE
            user_input_media[index] = Media(user_input_media[index], 'movie')
            user_input_media[index].genres = set(user_input_media[index].genres)
            # by default, genres for movie entries stored in a list. Needed to convert to a set
    return user_input_media
