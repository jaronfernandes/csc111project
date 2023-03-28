"""Makes sure this file is only run after 'datasets/filtered/keyword_graph.txt' is made"""
# TODO: media dataclass, compare function, other helper functions, read keywords graph function
from __future__ import annotations
import graph_classes
from typing import Optional


with open('datasets/filtered/keyword_graph.txt', 'r') as f:
    lines = f.readlines()
keyword_graph = graph_classes.Graph()
edges = eval(lines[1])
keyword_graph.add_all_edges(edges)


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
        self.genres = entry['genre']
        self.rating = float(entry['rating'])
        self.date = int(entry['release_date'][:4])
        self.synopsis = entry['plot_summary']
        self.keywords = entry['keywords']
        self.recommendation = set()

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
