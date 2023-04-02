"""Code for the graph"""
from __future__ import annotations
from typing import Any
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
        """gets the item values of all the vertices that are neighbours with this vertex
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
            # (for loop version)
            for u in self.neighbours:
                if u not in visited:
                    if u.check_connected(target_item, visited):
                        return True
            return False


class Graph:
    """A graph.
    Representation Invariants:
        - for each key in self._vertices, the corresponding vertex's item attribute
          equals that key
    """
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
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
        """Return the number of edges in this graph."""
        total_degree = sum(len(self._vertices[item].neighbours) for item in self._vertices)
        return total_degree // 2

    def get_neighbour_map(self) -> dict[Any, tuple]:
        """gets a dictionary for vertex item to a tuple of its neighbours"""
        return {self._vertices[x].item: tuple(self._vertices[x].get_neighbours()) for x in self._vertices}

    def connected(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are connected vertices
        in this graph.
        Return False if item1 or item2 do not appear as vertices
        in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return v1.check_connected(item2, set())
        else:
            return False

    def is_connected_graph(self) -> bool:
        """Return whether this graph is connected
        i.e. for all u, v in this graph's vertices, there exists a path
        This function uses graph theorems to simplify it
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
        """Finds shortest path with BFS. Length of path is number of vertices, not edges.

        PROCESS:
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

        INTUITION:
            - Goes level by level until end is reached. This means that the first time end is reached, we have the
            shortest path.
        """
        if self.connected(start, end):
            tracker = Queue()
            visited = set()

            current_node = self._vertices[start]

            # Queue initial path.
            tracker.put([current_node])

            while tracker:
                current_path = tracker.get()
                current_node = current_path[-1]
                visited.add(current_node)

                if current_node.item == end:
                    path = [node.item for node in current_path]
                    return len(path), path

                for neighbour in current_node.neighbours:
                    if neighbour not in visited:
                        tracker.put(current_path + [neighbour])
        else:
            return False
