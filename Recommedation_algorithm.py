"""Makes sure this file is only run after 'datasets/filtered/keyword_graph.txt' is made"""
#TODO: course dataclass, compare function, other helper functions, read keywords graph function
import graph_classes

with open('datasets/filtered/keyword_graph.txt', 'r') as f:
    lines = f.readlines()
keyword_graph = graph_classes.Graph()
edges = eval(lines[1])
keyword_graph.add_all_edges(edges)
