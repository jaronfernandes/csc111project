"""The main file, which the user must run to start the program.
This file should mostly just import the other files, and do some function calling to start up the program
"""
from __future__ import annotations

import graph_classes
import Recommedation_algorithm
import filter_movies

import testpyqt


def build_keyword_graph_from_file() -> graph_classes.Graph:
    """makes the graph to be used in the keywords assessment"""
    with open('datasets/filtered/keyword_graph.txt', 'r') as f:
        lines = f.readlines()
    keyword_graph = graph_classes.Graph()
    edges = eval(lines[1])
    vertices = eval(lines[0])
    for vertex in vertices:
        keyword_graph.add_vertex(vertex)
    keyword_graph.add_all_edges(edges)
    return keyword_graph


def get_recommendations(input_set: set[tuple[dict, str]], num_rec: int) -> list[Recommedation_algorithm.Media]:
    """
    every dict in the input_set is a valid entry format (json entry, form)
    """
    anime_list = filter_movies.load_json_file('datasets/filtered/final_animes.json')
    anime_media_list = []
    input_media_set = set()
    keyword_graph = build_keyword_graph_from_file()
    for item in input_set:
        input_media_set.add(Recommedation_algorithm.Media(item[0], item[1]))

    for anime in anime_list:
        anime_media = Recommedation_algorithm.Media(anime, 'anime')
        rec_score = 0
        full_score = 0
        for item in input_media_set:
            sim_score = anime_media.compare(item, input_media_set, keyword_graph)
            if anime_media.type == 'movie':
                rec_score /= 2
                full_score += 0.5
            else:
                full_score += 1
            rec_score += sim_score
        rec_score /= full_score
        anime_media.recommendation.add((input_media_set, rec_score))
        anime_media_list.append(anime_media)

    anime_media_list.sort(key=get_anime_rec_score)
    if num_rec <= len(input_set):
        return anime_media_list[0:num_rec]
    else:
        return anime_media_list


def get_anime_rec_score(anime: Recommedation_algorithm.Media, input_set: set[Recommedation_algorithm.Media]):
    """used for sorting the finalized anime list"""
    for recommendation in anime.recommendation:
        if input_set in recommendation:
            return recommendation[0]  # this should be the rec_score
