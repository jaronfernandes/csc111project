"""
Module description
===============================

This Python module is responsible for implementing the graph and vertex classes used to store keyword vertices. It
implements a shortest_path method using a breadth-first search algorithm that is central to our final recommendation
algorithm. It also implements various other helpful methods in both the vertex and graph classes that are useful in
creating our final keyword graph.

This file is Copyright (c) 2023 Jaron Fernandes, Ethan Fine, Carmen Chau, Jaiz Jeeson
"""
from __future__ import annotations
from typing import Any

# This is used in the shortest_path method of the Graph class.
from queue import Queue


class _Vertex:
    """A vertex in a graph.

    Instance Attributes:
        - item: The data stored in this vertex.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
    """
    item: Any
    neighbours: set[_Vertex]

    def __init__(self, item: Any, neighbours: set[_Vertex]) -> None:
        """Initialize a new vertex with the given item and neighbours."""
        self.item = item
        self.neighbours = neighbours

    def get_neighbours(self) -> set:
        """Gets items of all neighbours of self.
        """
        return {x.item for x in self.neighbours}

    def check_connected(self, target_item: Any, visited: set[_Vertex]) -> bool:
        """Return whether this vertex is connected to a vertex corresponding to target_item,
        by a path that DOES NOT use any vertex in visited.

        Preconditions:
            - self not in visited
        """
        if self.item == target_item:
            return True
        else:
            visited.add(self)
            for u in self.neighbours:
                if u not in visited:
                    if u.check_connected(target_item, visited):
                        return True
            return False


class Graph:
    """Graph class.

    Instance Attributes:
        - _vertices: set of vertices in the graph

    Representation Invariants:
        - For each key in self._vertices, the corresponding vertex's item attribute
          equals that key
    """
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges).
        """
        self._vertices = {}

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item to this graph.
        The new vertex is not adjacent to any other vertices.

        Preconditions:
            - item not in self._vertices
        """
        new_vertex = _Vertex(item, set())
        self._vertices[item] = new_vertex

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.
        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def add_all_edges(self, edges: set[tuple[Any, Any]]) -> None:
        """Add all given edges to this graph.

        Preconditions:
        - all(edge[0] != edge[1] for edge in edges)
        """
        for edge in edges:
            for item in edge:
                if item not in self._vertices:
                    self.add_vertex(item)
            self.add_edge(edge[0], edge[1])

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.
        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def num_edges(self) -> int:
        """Return the number of edges in this graph.
        """
        total_degree = sum(len(self._vertices[item].neighbours) for item in self._vertices)
        return total_degree // 2

    def get_neighbour_map(self) -> dict[Any, tuple]:
        """Returns a dictionary mapping the item at every vertex to a tuple of the items at its neighbours.
        """
        return {self._vertices[x].item: tuple(self._vertices[x].get_neighbours()) for x in self._vertices}

    def connected(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are connected vertices in this graph.
        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return v1.check_connected(item2, set())
        else:
            return False

    def is_connected_graph(self) -> bool:
        """Return whether this graph is connected, i.e., for all u, v in this graph's vertices, there exists a path.
        """
        n = len(self._vertices)
        e = self.num_edges()
        if e >= (n - 1) * (n - 2) // 2 + 1:
            return True
        elif e < n - 1:
            return False
        else:
            return all(self.connected(u, v) for u in self._vertices for v in self._vertices)

    def shortest_path(self, start: Any, end: Any) -> tuple[int, list] | bool:
        """Finds the shortest path from vertex with item start to vertex with item end using a Breadth First Search.

        If start and end are connected, function returns a tuple of two items - an integer representing the length of
        the shortest path, measured as the number of vertices in the path, and a list representing the path itself,
        containing the vertices in the path. Otherwise, function returns False.

        Process:
             - Track paths, not nodes as in naive BFS
             - Start queue with a path that has only start
             - Until queue is empty
                - Add current node to visited
                - Add current no
                - Get latest path
                - Get latest node in path
                - If latest node is already end, return
                - If latest node is not already end, add new paths to the queue incremented by neighbours that haven't
                been visited.
                - Repeat

        Intuition:
            - Goes level by level until end is reached. This means that the first time end is reached, we have the
            shortest path.
        """
        if self.connected(start, end):
            tracker = Queue()
            visited = set()

            # Find vertex corresponding to start
            current_node = self._vertices[start]

            # Queue initial path - consists only of one vertex, that corresponding to start.
            tracker.put([current_node])

            # Iterate till the tracker is empty.
            while tracker:
                # Get least recently added path and the farthest vertex from it.
                current_path = tracker.get()
                current_node = current_path[-1]
                visited.add(current_node)

                # Return path if we are currently at end.
                if current_node.item == end:
                    path = [node.item for node in current_path]
                    return len(path), path

                # Queue new paths, where a new path is created if current_node's neighbours have not yet been visited.
                for neighbour in current_node.neighbours:
                    if neighbour not in visited:
                        tracker.put(current_path + [neighbour])

            return False
        # If start and end are not connected by a path, there is no shortest path.
        else:
            return False


if __name__ == '__main__':

    # Enabling python_ta configurations:
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['queue'],
        'allowed-io': [''],
        'disable': [''],
        'max-nested-blocks': 4,
        'max-line-length': 120,
    })
