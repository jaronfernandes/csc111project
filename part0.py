"""Test Project

This also includes the Priority Queue class.

The Priority Queue code was taken from CSC110/CSC111 Lecture Notes 10.8,
https://www.teach.cs.toronto.edu/~csc110y/fall/notes/10-abstraction/08-priority-queues.html,
authored by David Liu et al.

Dijkstra's algorithm code was referenced from SpanningTree and Wikipedia:
    - https://www.youtube.com/watch?v=EFg3u_E6eHU and
    - https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm

Please let me know if you want to clarify/modify/improve on anything in here!
"""
from __future__ import annotations

import math
from typing import Any, Optional

# ============================================================================
# PRIORITY QUEUE CODE
# ============================================================================


class EmptyPriorityQueueError(Exception):
    """Exception raised when calling pop on an empty priority queue."""

    def __str__(self) -> str:
        """Return a string representation of this error."""
        return 'You called dequeue on an empty priority queue.'


class PriorityQueue:
    """A queue of items that can be dequeued in priority order.

    When removing an item from the queue, the LOWEST-priority item is the one
    that is removed.
    """
    # Private Instance Attributes:
    #   - _items: a list of the items in this priority queue
    _items: list[tuple[int, Any]]

    def __init__(self) -> None:
        """Initialize a new and empty priority queue."""
        self._items = []

    def is_empty(self) -> bool:
        """Return whether this priority queue contains no items.
        """
        return self._items == []

    def dequeue(self) -> Any:
        """Remove and return the item with the LOWEST priority.

        Raise an EmptyPriorityQueueError when the priority queue is empty.
        """
        if self.is_empty():
            raise EmptyPriorityQueueError
        else:
            _priority, item = self._items.pop()
            return item

    def enqueue(self, priority: int, item: Any) -> None:
        """Add the given item with the given priority to this priority queue.

        Preconditions:
            - self.priority >= 0
        """
        i = len(self._items) - 1
        while i > 0 and self._items[i][0] > priority:
            # Loop invariant: all items in self._items[0:i]
            # have a HIGHER priority than <priority>.
            i = i - 1

        self._items.insert(i, (priority, item))


# ============================================================================
# GRAPH AND VERTEX CODE
# ============================================================================


# TODO: May need to potentially add an 'id' attribute for _Vertex.
class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The name of the movie stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.
        - type: The type of show the vertex is of: an anime or a movie.
        - genres: A list of genres associated with the media.
        - synopsis: A synopsis of the media.
        - start_end_year: The release year of the media and possibly the end year if it has one.
        - rating: A popularity rating of the media.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.type == 'Anime' or self.type == 'Movie'
        - 0.0 <= self.rating <= 10.0
        - all(0.0 <= self.neighbours[x][0] <= 1.0 for x in self.neighbours)  # score
        - all(0.0 <= self.neighbours[x][1] <= 1.0 for x in self.neighbours)  # synopsis similarity
        - all(0.0 <= self.neighbours[x][2] <= 1.0 for x in self.neighbours)  # genre similarity
        - all(0.0 <= self.neighbours[x][3] <= 1.0 for x in self.neighbours)  # release similarity
        - all(0.0 <= self.neighbours[x][4] <= 1.0 for x in self.neighbours)  # rating similarity
    """
    item: Any
    neighbours: dict[_Vertex, tuple[float, float, float, float, float]]
    # tuple is (total score, synopsis similarity, genre similarity, release similarity, rating similarity)
    type: str
    genres: list[str]
    synopsis: str
    start_end_year: str
    rating: Optional[float]

    def __init__(self, item: Any, type: str, synopsis: str, genres: list[str],
                 start_end_year: str, rating: Optional[float] = None) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.type = type
        self.synopsis = synopsis
        self.genres = genres
        self.start_end_year = start_end_year
        self.rating = rating
        self.neighbours = {}

    def get_details(self) -> tuple[str, list[str], str, Optional[float]]:
        """Returns important statistics about the vertex in the form of a tuple.

        Useful for similarity algorithms.
        """
        return (self.synopsis, self.genres, self.start_end_year, self.rating)


class RecommendationGraph:
    """A graph.

    Representation Invariants:
        - all(item == self._vertices[item].item for item in self._vertices)
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def get_vertex(self, item: Any) -> Optional[_Vertex]:
        """Returns the given vertex.
        If there is no corresponding vertex, it returns None.
        """
        if item in self._vertices:
            return self._vertices[item]
        else:
            return None

    def add_vertex(self, info_row: list[str]) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - info_row[0] is the name of the media
            - info_row[1] is the type of the media
            - info_row[1] == 'Anime' or info_row[1] == 'Movie'
            - info_row[2] is a string that represents the synopsis
            - info_row[3] is a string that represents a sequence of strings that contain all the genres
            - info_row[4] is the release year and possibly end year
            - info_row[5] is a valid rating, or None if there is not one.
        """
        if info_row[0] not in self._vertices:
            genres = info_row[3].split(',')
            year = (info_row[4])

            # FIXME: It's not just the rating part of the TV Series.csv data set
            #  that has '****'; it can be others too. We should fix or implement
            #  some check way to circumvent this and update the instance attributes
            #  for a more accurate calculate_connection() call.

            if info_row[5] == '****' or info_row[5] == '':
                # Edge "unfilled" cases that I've encountered in the IMDB/Anime sets.
                # We just set it to None, and then the function that calculates the conneciton will just
                # ignore the rating part at the moment.
                # FIXME: If we don't want to totally ignore the rating if there isn't one, then we can
                #  make it negatively affect the connection calculation. At the moment, the connection
                #  calculation is simply done without rating if there isn't one.
                rating = None
            else:
                rating = float(info_row[5])

            self._vertices[info_row[0]] = \
                _Vertex(
                    info_row[0],
                    info_row[1],
                    info_row[2],
                    genres,
                    year,
                    rating,
                )

    def add_edge(self, item1: Any, item2: Any, connection: tuple[float, float, float, float, float]) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new edge
            v1.neighbours[v2] = connection
            v2.neighbours[v1] = connection
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError

    def get_shortest_path_dijkstra(self, starting_vertex: Any) -> list[_Vertex]:
        """Method that returns the shortest path based on connections using Dijkstra's algorthim.

        Heavily references to https://www.youtube.com/watch?v=EFg3u_E6eHU and
        https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
        Preconditions:
            - starting_vertex in self._vertices
        """
        # TODO: Add citations for Dijkstra's.
        # TODO/FIXME: I have not tested this method yet, so I don't know if it works.
        distances = {}
        prev = {}
        unexplored = {}
        start = self._vertices[starting_vertex]
        queue = PriorityQueue()

        for vertex in self._vertices:
            if vertex is not start:
                distances[vertex] = math.inf  # Initialize every vertex to infinity, EXCEPT for the starting vertex.
            else:  # vertex is start
                distances[start] = 0

            prev[vertex] = None  # We set the previous vertex of each vertex to None, as we haven't visited anything yet
            unexplored[vertex] = True  # Set every vertex to "unexplored"
            queue.enqueue(distances[vertex], vertex)  # Add each vertex to the Priority Queue.

        while not queue.is_empty():  # Repeats the loop body until the Priority Queue IS EMPTY
            closest_vertex = queue.dequeue()
            unexplored.pop(closest_vertex)  # We explore the vertex that is closest to us.

            for neighbour in self._vertices[closest_vertex].neighbours:  # Check every neighbour in this vertex.
                if neighbour in unexplored:  # Check if we haven't explored this neighbour vertex yet.
                    # Calculate the distance for a potentially closer path to the neighbour vertex.
                    potential_path = distances[closest_vertex] + closest_vertex.neighbours[neighbour][0]

                    if potential_path < distances[neighbour]:  # If we've found a shorter path, update the distance!
                        distances[neighbour] = potential_path
                        prev[neighbour] = closest_vertex

        # TODO: Formulate a way to return a list of the shortest path.
        return ...
