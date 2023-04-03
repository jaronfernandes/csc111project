"""CSC111 Course Project: main.py

Module description
===============================
The main file, which the user must run to start the program.
This file should mostly just import the other files, and do some function calling to start up the program.

This Python module is also responsible for creating and displaying all the necessary UI related to the project,
using PyQt6 to create an application loaded with several widgets, images, labels, and layouts.
Utilizes a function that takes in stylesheets to beautify the application.

This file is Copyright (c) 2023 Jaron Fernandes, Ethan Fine, Carmen Chau, Jaiz Jeeson
"""
from __future__ import annotations

import csv

from typing import Optional

import json
import random
import os
import sys

import requests  # You must have an internet connection

import python_ta
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QGroupBox, QFormLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QMainWindow, QLineEdit, QCompleter, QScrollArea, QSpacerItem, QSizePolicy, QApplication
)

from PyQt6.QtGui import QFont, QPixmap, QImage
from PyQt6 import QtCore
from recommendation_algorithm import Media
import graph_classes
import recommendation_algorithm
import filter_movies
import anime_filter

# Picks a random background image at the start of the program and excludes the .DS_Store path.
BACKGROUND_IMAGE = \
    f"imgs/background_images/{random.choice([x for x in os.listdir('imgs/background_images') if x[0] != '.'])}"
ALL_GENRES = anime_filter.get_genres()


def build_keyword_graph_from_file() -> graph_classes.Graph:
    """Makes the graph to be used in the keywords assessment"""
    with open('datasets/filtered/keyword_graph.txt', 'r') as f:
        lines = f.readlines()
    keyword_graph = graph_classes.Graph()
    edges = eval(lines[1])
    vertices = eval(lines[0])
    for vertex in vertices:
        keyword_graph.add_vertex(vertex)
    keyword_graph.add_all_edges(edges)
    return keyword_graph


def modified_get_recommendations(input_set: list[tuple[dict, str]], num_rec: int, rating: float, genres: set[str]) -> \
        list[recommendation_algorithm.Media]:
    """
    Generates a list of anime recommendations for the user.

    Preconditions:
    - every dict in the input_set is a valid entry format (json entry, form)
    """
    anime_list = filter_movies.load_json_file_animes('datasets/filtered/final_animes.json')
    anime_list = (anime_list, anime_list.copy())

    for anime in anime_list[0]:
        if float(anime['rating']) < rating or not all(genre in anime['genre'] for genre in genres):
            anime_list[1].remove(anime)

    anime_list = anime_list[1]

    anime_media_list = []
    input_media_set = set()
    keyword_graph = build_keyword_graph_from_file()
    for item in input_set:
        input_media_set.add(recommendation_algorithm.Media(item[0], item[1]))

    count = 0
    for anime in anime_list:
        anime_media = recommendation_algorithm.Media(anime, 'anime')
        rec_score = 0
        full_score = 0
        for item in input_media_set:
            sim_score = anime_media.compare(item, input_media_set, keyword_graph)
            if anime_media.type == 'movie':
                sim_score /= 2
                full_score += 0.5
            else:
                full_score += 1
            rec_score += sim_score
        rec_score /= full_score
        anime_media.recommendation['thing'] = (rec_score, input_media_set)
        anime_media_list.append(anime_media)
        # print(count + 1)
        count += 1
        # if count == 10:  # Remove during actual submission
        #     break

    anime_media_list.sort(key=lambda anime: get_anime_rec_score(anime, input_media_set))
    if num_rec <= len(anime_media_list):  # uhhhh what?
        return anime_media_list[0:num_rec]
    else:
        return anime_media_list  # i edited this cause otherwise it's gonna put the ENTIRE anime list


def get_anime_rec_score(anime: recommendation_algorithm.Media, input_set: set[recommendation_algorithm.Media]) -> float:
    """Used for sorting the finalized anime list"""
    for recommendation in anime.recommendation:
        if input_set in anime.recommendation[recommendation]:
            return anime.recommendation[recommendation][0]  # this should be the rec_score

    return 0.0  # This should never run though bc we are certain the if condition in the loop will execute once.


def extract_movies_file(filename: str) -> tuple[dict[str, str], dict[str, dict]]:
    """Helper function associated with extracting movies and shows from the final IMDB files in the filtered datasets.

    Preconditions:
    - filename is the path of a valid readable JSON file
    """
    names = {}
    json_lines = {}

    with open(filename, 'r') as f:
        string = f.read()
        for line in json.loads(string):
            if 'movie' in filename:
                names[line['title']] = 'Movie'
                json_lines[line['title']] = line
            elif 'show' in filename:
                names[line['title']] = 'Show'
                json_lines[line['title']] = line

    return names, json_lines


def extract_images_file() -> dict[str, str]:
    """Extracting images for animes through the AnimeList.csv dataset.
    Manipulates the invalid image URLs into valid (working) ones
    """
    images = {}

    with open('datasets/raw/AnimeList.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)

        next(reader)

        for row in reader:
            # Loop Invariant:
            assert row[5] == '' or row[5].find('anime/') == 40  # row[5] is not an empty str ==> index is 40

            images[row[1]] = 'https://cdn.myanimelist.net/images/anime/' + row[5][46:]

    return images


class AnimeWidget(QWidget):
    """Widget for each recommended anime.

    Instance Attributes:
    - anime_data: The media object which contains all the data regarding the anime
    - full_description: The entire description (plot synopsis) of the anime.
    - image: A QPixmap image used to show the anime icon from MAL.
    - layout: A vertical layout for organizing the items of the anime recommendation.
    - left: An AnimeWidget node.
    - left_button: A QPushbutton to swap to the recommended anime on the left.
    - parent: The parent window of this widget.
    - position: The ranking in which this anime was recommended.
    - right: An AnimeWidget node.
    - right_button: A QPushbutton to swap to the recommended anime on the right.
    - title: The QLabel used for representing the anime title.

    Representation Invariants:
    - self.anime_data is a valid Media object for the anime associated with this widget.
    - self.position >= 1
    """
    anime_data: Media
    # box: QGroupBox
    # form_layout: QFormLayout
    full_description: str
    description: QLabel
    image: Optional[QPixmap]
    layout: QVBoxLayout
    left: Optional[AnimeWidget]
    left_button: QPushButton
    parent: MainWindow
    position: int
    right: Optional[AnimeWidget]
    right_button: QPushButton
    title: QLabel

    def __init__(self, anime_data: Media, parent: MainWindow, position: int) -> None:
        """Initializes the AnimeWidget.

        Preconditions:
        - anime_data is a valid Media object with the appropriate instance attributes for this anime widget.
        - position >= 1
        """
        super().__init__()
        self.parent = parent
        self.anime_data = anime_data
        self.full_description = anime_data.synopsis
        self.description = QLabel(anime_data.synopsis)
        self.description.setWordWrap(True)
        self.description.setFont(QFont('Avenir', 20))
        self.layout = QVBoxLayout()
        self.title = QLabel(anime_data.title)
        self.position = position
        self.left = None
        self.right = None
        self.left_button = QPushButton('<')
        self.left_button.setFixedSize(QtCore.QSize(40, 40))
        self.right_button = QPushButton('>')
        self.right_button.setFixedSize(QtCore.QSize(40, 40))

        # self.title.move(self.parent.rect().center())
        # self.title.move(50, 50)

        self.layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignHCenter)
        # self.layout.addWidget(QLabel('\n\n'), alignment=Qt.AlignmentFlag.AlignHCenter)
        spacer2 = QSpacerItem(0, 50, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addItem(spacer2)  # SPACER IS IMPORTANT FOR MAKING THE < > ARROWS DETACHED!!!
        # self.layout.addWidget(self.description)

        # self.box = QGroupBox()
        # self.form_layout = QFormLayout()

        # self.form_layout.addRow(self.left_button, self.right_button)

        # self.box.setLayout(self.form_layout)

        # Attempting to find an image (within a try-except in-case internet or image does not exist)
        image = QImage()
        try:
            url = self.parent.movie_images[self.title.text()]
            image.loadFromData(requests.get(url).content)
        except (KeyError, ConnectionError, requests.exceptions.ConnectionError):
            image = QPixmap('imgs/sadge.jpeg')
        finally:
            self.title.setPixmap(QPixmap(image))
            self.title.setScaledContents(True)
            self.title.setFixedSize(250, 250)

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer)  # SPACER IS IMPORTANT FOR MAKING THE < > ARROWS DETACHED!!!

        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.description)
        scroll.setLayout(QVBoxLayout())
        # self.scroll.verticalScrollBar().setStyleSheet(
        #     """QScrollBar {
        #         color: transparent !important;
        #         opacity: 0;
        #     }"""
        # )
        # self.scroll.setStyleSheet(
        #     """QScrollArea {
        #         border: none;
        #         background-color: transparent !important;
        #     }""")

        self.setStyleSheet("""
        QLabel {
            border: none;
            background: none;
            background-color: transparent !important;
            opacity: 0;
        }""")

        self.layout.addWidget(scroll)

        #  self.submit_button.setFixedSize(QtCore.QSize(200, 40))
        # self.layout.addWidget(self.left_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # This is to center the < and > buttons at the bottom of the window
        deez = QFormLayout()
        deez.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        deez.addRow(self.left_button, self.right_button)
        self.layout.addLayout(deez)

        # if image is not None:
        #     self.image = QPixmap('imgs/samplegradient.jpeg')
        #     self.title.setPixmap(self.image)

        self.title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.description.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(self.layout)

        self.right_button.clicked.connect(self.switch_animes_right)
        self.left_button.clicked.connect(self.switch_animes_left)

    def switch_animes_left(self) -> None:
        """Button Events to switch the anime recommendation left through LinkedList"""
        self.hide()
        self.parent.recommendation_box.setTitle(
            str(self.left.position) + ') Recommended Anime: ' + self.left.anime_data.title)
        self.left.show()

    def switch_animes_right(self) -> None:
        """Button Events to switch the anime recommendation right through LinkedList"""
        self.hide()
        self.parent.recommendation_box.setTitle(
            str(self.right.position) + ') Recommended Anime: ' + self.right.anime_data.title)
        self.right.show()


class ListWidgetTemplate(QWidget):
    """A widget class that can be used by its subclasses as widgets that can be added and removed to lists.

    Instance Attributes:
    - name: The name of the movie/show.
    - type: The QLabel associating to the type (either movie or show)
    - label: The QLabel associated with the name of the movie or show.
    - close_button: The QPushButton object used to remove the item from the list.
    - layout: The layout for this widget
    - parent: The parent that this object is linked to (MainWindow)

    Representation Invariants:
    - self.name is a valid movie/show name.
    - self.type in {'Movie', 'Show'}
    """
    name: str
    label: QLabel
    close_button: QPushButton
    layout: QHBoxLayout
    parent: MainWindow

    def __init__(self, name: str, parent: MainWindow) -> None:
        """The initializer to create an object.

        Preconditions:
        - name is a valid movie/show name
        - movie_type in {'Movie', 'Show'}
        """
        super().__init__()
        self.parent = parent

        # self.setMaximumHeight(50)
        self.name = name
        self.label = QLabel(self.name, self)
        self.label.setWordWrap(True)
        self.close_button = QPushButton('X', self)
        self.close_button.setFixedSize(QtCore.QSize(40, 40))
        self.close_button.setFont(QFont('Avenir', 30))

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.close_button.clicked.connect(self.on_clicked)

    def on_clicked(self) -> None:
        """
        To be inherited by subclasses.
        """
        raise NotImplementedError


class MovieWidget(ListWidgetTemplate):
    """Widget for each movie in the dropdown.

    Instance Attributes:
    - name: The name of the movie/show.
    - type: The QLabel associating to the type (either movie or show)
    - label: The QLabel associated with the name of the movie or show.
    - close_button: The QPushButton object used to remove the item from the list.
    - layout: The layout for this widget
    - parent: The parent that this object is linked to (MainWindow)

    Representation Invariants:
    - self.name is a valid movie/show name.
    - self.type in {'Movie', 'Show'}
    """
    type: QLabel

    def __init__(self, name: str, parent: MainWindow, movie_type: str) -> None:
        """The initializer to create an object.

        Preconditions:
        - name is a valid movie/show name
        - movie_type in {'Movie', 'Show'}
        """
        super().__init__(name, parent)
        self.type = QLabel('Type: ' + movie_type)
        self.type.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.type)
        self.layout.addWidget(self.close_button)

        self.close_button.clicked.connect(self.on_clicked)

    def on_clicked(self) -> None:
        """Method that removes itself when the button is clicked.
        This *should* be garbage collected as there is no reference to it (?)
        """
        self.parent.added_movies.remove(self.name)
        self.layout.removeWidget(self)
        # print(self.parent.added_movies)
        # self.destroy()


class GenreWidget(ListWidgetTemplate):
    """Widget for each movie in the dropdown.

    Instance Attributes:
    - name: The name of the movie/show.
    - label: The QLabel associated with the name of the movie or show.
    - close_button: The QPushButton object used to remove the item from the list.
    - layout: The layout for this widget
    - parent: The parent that this object is linked to (MainWindow)

    Representation Invariants:
    - self.name is a valid movie/show name.
    """

    def __init__(self, name: str, parent: MainWindow) -> None:
        """The initializer to create an object.

        Preconditions:
        - name in ALL_GENRES
        """
        super().__init__(name, parent)
        self.layout.addWidget(self.close_button)

    def on_clicked(self) -> None:
        """Method that removes itself when the button is clicked.
        This *should* be garbage collected as there is no reference to it (?)
        """
        self.parent.settings[7].remove(self.name)
        self.layout.removeWidget(self)


class MainWindow(QMainWindow):
    """Main window for the application.

    Instance Attributes:
    - add_movie_button: A QPushButton responsible for adding a MovieWidget to the displayed list.
    - added_movies: A set that contains the list of currently selected movie/show names.
    - container: A container that aids with the layout.
    - container_layout: A layout that organizes the positions of its children widgets.
    - form_layout: A layout used for adding multiple elements on a single horizontal row.
    - json_movies: A dictionary that holds each movie entry from its filtered dataset.
    - movies: A dict of all the movies extracted from the dataset.
    - movie_images: The images of all the animes as extracted from the dataset.
    - recommended_animes: A dictionary holding every AnimeWidget and its associated key (the anime name)
    - recommendation_box: A QGroupBox that stores holds all the AnimeWidgets.
    - scroll: A scroll object used to scroll through the recommendation_box when it gets too large.
    - searchbar: A QLineEdit object used for the user to search up movies/shows.
    - settings: A list that holds customizable objects for the user to fine-tune their recommendation search. It
    contains the rating_text_object, a float of the minimum rating, select_rating_button, num_animes_text object, an int
    of the number of animes to recommend, select_num_animes_button, ...
    - submit_button: The button that fires a signal when the user wants to generate recommendations.

    Representation Invariants:
    - every movie in self.movies is from the filtered dataset.
    - every image in self.movie_images is a url (that can be manipulated).
    - self.added_movies contains movies and shows from the filtered dataset.
    - every dict in json_movies corresponds to a dict in one of the final IMDB movies/shows filtered datasets.
    """
    add_movie_button: QPushButton
    added_movies: set
    container: QWidget
    container_layout: QVBoxLayout
    form_layout: QFormLayout
    json_movies: dict
    movies: dict
    movie_images: dict[str, str]
    recommended_animes: dict
    recommendation_layout: QFormLayout
    recommendation_box: QGroupBox
    scroll: QScrollArea
    searchbar: QLineEdit
    settings: list
    submit_button: QPushButton

    def __init__(self) -> None:
        """Initializes the MainWindow."""
        super().__init__()

        self.setWindowTitle('Anime Recommendation System')
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.searchbar = QLineEdit()
        self.searchbar.setFixedSize(QtCore.QSize(200, 40))
        self.add_movie_button = QPushButton('Add Movie or Show')
        self.add_movie_button.setFixedSize(QtCore.QSize(200, 40))
        self.form_layout = QFormLayout()
        self.recommended_animes = {}
        self.recommendation_box = QGroupBox('Recommended Anime:')
        self.recommendation_layout = QFormLayout()
        self.settings = [
            QLineEdit(), 0.0, QPushButton(),  # For minimum rating (indices 0 - 2)
            QLineEdit(), 3, QPushButton(),  # For number of animes to recommend (indices 3 - 5)
            QLineEdit(), set(), QPushButton(), QScrollArea(), QFormLayout()  # For whitelisting genres (indices 6 - 10)
        ]
        self.scroll = QScrollArea()
        self.added_movies = set()

        movie_names, json_lines = extract_movies_file('datasets/filtered/final_imdb_movies.json')
        extracted_shows, json_shows = extract_movies_file('datasets/filtered/final_imdb_shows.json')
        movie_names.update(extracted_shows)
        json_lines.update(json_shows)

        self.movies = movie_names
        self.json_movies = json_lines
        self.movie_images = extract_images_file()

        # To space the drop-down.
        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.container_layout.addItem(spacer)
        self.container.setLayout(self.container_layout)

        # Create the auto-complete
        completer = QCompleter(self.movies)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.searchbar.setCompleter(completer)

        # Scroll Area Properties.
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)

        # Customizing the Recommendation box:
        self.recommendation_box.setFont(QFont('Avenir', 30))
        self.recommendation_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.recommendation_box.setLayout(self.recommendation_layout)

        # Customizable Settings Widgets (Minimum Rating Animes to Choose From)
        self.settings[0].setFixedSize(QtCore.QSize(200, 40))
        self.settings[0].setPlaceholderText('7.4 - 10.0')
        self.settings[2].setText('Set Minimum Rating')
        self.settings[2].setFixedSize(QtCore.QSize(200, 40))
        # Customizable Settings Widgets (Minimum # of Animes to Recommend)
        self.settings[3].setFixedSize(QtCore.QSize(200, 40))
        self.settings[3].setPlaceholderText('Current: 3 Range: 1+')
        self.settings[5].setText('Set # to Recommend')
        self.settings[5].setFixedSize(QtCore.QSize(200, 40))
        # Customizable Settings Widgets (Whitelisting Genres)
        self.settings[6].setFixedSize(QtCore.QSize(200, 40))
        self.settings[6].setPlaceholderText('Ex. Comedy')
        self.settings[8].setText('Add Genre to Whitelist')
        self.settings[8].setFixedSize(QtCore.QSize(200, 40))
        # Setting up the scroll area for the genre list.
        self.settings[9].setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.settings[9].setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.create_interface()

    def create_interface(self) -> None:
        """Helper method to continue creating the interface."""
        # Group Box
        group_box = QGroupBox('Movies and Shows Added')
        group_box.setFont(QFont('Avenir', 30))

        group_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        group_box.setLayout(self.form_layout)

        self.scroll.setWidget(group_box)
        # self.container_layout.addWidget(anime_box)

        # Creating the container
        container = QWidget()
        container_layout = QVBoxLayout()
        row = QFormLayout()
        row.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        row.addRow(self.searchbar, self.add_movie_button)

        genres_box = QGroupBox('Whitelisted Genres:')
        genres_box.setFont(QFont('Avenir', 30))
        genres_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        genres_box.setLayout(self.settings[10])

        # Continued customization of the genre scroll (because python-ta is complaining about exceeding 50 statements)
        self.settings[9].setWidgetResizable(True)
        self.settings[9].setWidget(genres_box)

        # Genre auto-complete
        genre_completer = QCompleter(ALL_GENRES)
        genre_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.settings[6].setCompleter(genre_completer)

        row.addRow(self.settings[0], self.settings[2])
        row.addRow(self.settings[3], self.settings[5])
        row.addRow(self.settings[6], self.settings[8])
        row.addRow(self.settings[9])

        # container_layout.addLayout(row)

        selected_shows_layout = QVBoxLayout()

        self.scroll.setLayout(selected_shows_layout)
        container_layout.addWidget(self.scroll)
        # container_layout.addWidget(self.recommendation_box)

        self.recommendation_box.hide()

        self.submit_button = QPushButton('Submit')
        self.submit_button.setFixedSize(QtCore.QSize(200, 40))
        container_layout.addWidget(self.submit_button, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        container.setLayout(container_layout)

        main_container = QWidget()
        layoutttt = QHBoxLayout()
        layout_two = QVBoxLayout()

        # # To space the list of genres.
        # spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        # row.addItem(spacer)

        layoutttt.addWidget(container, stretch=1)
        layout_two.addLayout(row)
        layout_two.addWidget(self.settings[9])

        widgety = QWidget()
        widgety.setLayout(layout_two)
        layoutttt.addWidget(widgety)
        main_container.setLayout(layoutttt)

        self.setCentralWidget(main_container)

        # self.setCentralWidget(container)

        self.showMaximized()
        self.showFullScreen()

        self.add_movie_button.clicked.connect(self.on_movie_added)
        self.submit_button.clicked.connect(self.on_submit)
        self.settings[2].clicked.connect(self.set_rating)
        self.settings[5].clicked.connect(self.set_min_animes)
        self.settings[8].clicked.connect(self.on_genre_added)

    def on_movie_added(self) -> None:
        """Button event for when movies are added"""
        text = self.searchbar.text()
        if text in self.movies and text not in self.added_movies:
            self.searchbar.setText('')
            self.form_layout.addRow(MovieWidget(text, self, self.movies[text]))
            self.added_movies.add(text)
            # print(self.added_movies)

    def on_genre_added(self) -> None:
        """Button event for when genres are added"""
        text = self.settings[6].text()
        if text in ALL_GENRES and text not in self.settings[7]:
            self.searchbar.setText('')
            self.settings[10].addRow(GenreWidget(text, self))
            self.settings[7].add(text)

    def set_rating(self) -> None:
        """Button event for when the minimum rating filter is set"""
        min_rating = self.settings[0].text()
        try:
            min_rating = float(min_rating)
        except ValueError:
            if min_rating != '':
                self.settings[0].setPlaceholderText('Error: Not 7.4 - 10.0')
        else:
            if not 7.4 <= min_rating <= 10.0:
                self.settings[0].setPlaceholderText('Error: Not 7.4 - 10.0')
            else:
                self.settings[1] = min_rating
                self.settings[0].setPlaceholderText(str(min_rating))
        finally:
            self.settings[0].setText('')

    def set_min_animes(self) -> None:
        """Button event for when the number of animes to recommend is set.

        Sets the number of animes to recommend to the max of the min_num_animes provided and 1 (so no negatives)
        """
        min_animes = self.settings[3].text()
        try:
            min_animes = int(min_animes)
        except ValueError:
            pass
        else:
            self.settings[4] = max(min_animes, 1)
        finally:
            self.settings[3].setText('')
            self.settings[3].setPlaceholderText(f'Current: {self.settings[4]} Range: 1+')

    def on_submit(self) -> None:
        """Button event that triggers recommendation generation
        when the user submits their list of movies/shows.

        Preconditions:
        - The amount of recommended animes returned != 0
        """
        self.searchbar.hide()
        self.submit_button.hide()
        self.add_movie_button.hide()
        self.scroll.hide()
        self.setCentralWidget(self.recommendation_box)
        self.recommendation_box.show()

        lst = []

        if len(self.added_movies) == 0:
            self.recommendation_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.recommendation_box.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.recommendation_layout.addRow(
                QLabel("No animes to recommend! Please add some movies or shows you've watched for better results.")
            )
            self.recommendation_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.recommendation_box.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        else:
            # print('started')
            lst = modified_get_recommendations(
                [(self.json_movies[entry], self.movies[entry])
                 for entry in self.json_movies if entry in self.added_movies],
                self.settings[4],
                self.settings[1],
                self.settings[7]
            )
            # print('done')

            if len(lst) == 0:
                self.recommendation_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.recommendation_box.setAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.recommendation_layout.addRow(
                    QLabel('No animes to recommend! Try lessening your filters for better results.')
                )
                self.recommendation_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
                self.recommendation_box.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        print('Recommended Shows:',
              {anim.title: anim.__dict__ for anim in lst})
        print('Movies/shows Added:', self.added_movies)
        print('Rating Filter:', self.settings[1])
        print('Number of Animes to Recommend:', self.settings[4])
        print('Genre Whitelist:', self.settings[7])

        for i in range(0, len(lst)):
            anime = lst[i]

            if i == 0:
                self.recommendation_box.setTitle(f'{i + 1}) Recommended Anime: {anime.title}')
                self.recommended_animes[anime.title] = AnimeWidget(anime, self, i + 1)
                self.recommendation_layout.addRow(self.recommended_animes[anime.title])

            # centerPoint = QDesktopWidget().availableGeometry().center()
            # qtRectangle.moveCenter(centerPoint)
            # self.recommended_animes[anime.title] = QLabel(anime.title, self)
            # self.recommended_animes[anime.title].move(500, 100)
            # self.recommended_animes[anime.title].show()

            self.recommendation_layout.addRow(self.recommended_animes[anime.title])
            if i + 1 != len(lst):
                self.recommended_animes[lst[i + 1].title] = AnimeWidget(lst[i + 1], self, i + 2)
                self.recommended_animes[anime.title].right = self.recommended_animes[lst[i + 1].title]
            if i != 0:
                self.recommended_animes[anime.title].left = self.recommended_animes[lst[i - 1].title]
                self.recommended_animes[anime.title].hide()

        if len(lst) != 0:
            self.recommended_animes[lst[-1].title].right = self.recommended_animes[lst[0].title]
            self.recommended_animes[lst[0].title].left = self.recommended_animes[lst[-1].title]

        # SELF REMINDER THAT I CAN USE A DICTIONARY/LIST TO STORE ALL THE WIDGETS AFTER THE RECOMMENDED
        # ANIMES ARE GENERATED, AND THEN KEEP IT AND THEN HIDE/SHOW AS USERS SCROLL THROUGH EACH ONE.


app = QApplication(sys.argv)

# Note: background-size is not supported by PyQt6, which is why it doesn't work!
# For MainWindow, simply use MainWindow
app.setStyleSheet("""
    QMainWindow {"""f"""
        background-color: "white";
        border: none;
        font-family: "Avenir";
        background-image: url({BACKGROUND_IMAGE});
        background-repeat: no-repeat;
        border-image: url({BACKGROUND_IMAGE}) 0 0 0 0 stretch stretch;
        line-height: 20;
        opacity: 0;
    """"""}
    """"""
    AnimeWidget {
        opacity: 0;
        background: transparent !important;
        border: none;
    }
    QFormLayout {
        border: none;
        background: transparent !important;
        opacity: 0;
    }
    QGroupBox {
        background-color: "white";
        border: none;
        font-family: "Avenir";
        background: transparent !important;
        color: white;
        font-size: 30px;
        padding: 70px;
        opacity: 0;
    }
    QVGroupBox {
        background: transparent !important;
        opacity: 0;
    }
    AnimeWidget::QLabel {
        border: none;
        font-family: "Avenir";
        background: transparent !important;
        font-size: 30px;
        padding: 70px;
        opacity: 0;
    }
    QGroupBox::title {
        border: none;
        font-family: "Avenir";
        color: white;
        font-size: 30px;
        opacity: 0;
    }
    QFormLayout {
        opacity: 0;
    }
    QPushButton {
        font-size: 16px;
        font-family: "Avenir";
        background-color: "lightblue";
        border-collapse: separate;
        border-radius: 20%;
        opacity: 0;
    }
    MainWindow::QPushButton {
        font-size: 16px;
        font-family: "Avenir";
        background-color: "white";
        border-collapse: separate;
        border-radius: 4px;
        opacity: 0;
    }
    QLineEdit {
        background-color: "white";
        font-family: "Avenir";
        color: "black";
        opacity: 0;
    }
    QLabel {
        font-family: "Avenir";
        font-size: 25px;
        color: white;
        opacity: 0;
    }
    QScrollArea {
        opacity: 0;
        background: transparent !important;
    }
""")

w = MainWindow()
w.show()


if __name__ == '__main__':
    python_ta.check_all(config={
        'extra-imports': [
            'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtWidgets', 'PyQt6.QtGui', 'Qt', 'os', 'sys', 'random', 'json', 'QWidget',
            'QGroupBox', 'QFormLayout', 'QHBoxLayout', 'QVBoxLayout', 'QLabel', 'QPushButton', 'QMainWindow',
            'QLineEdit', 'QCompleter', 'QScrollArea', 'QFont', 'QPixmap', 'QtCore', 'recommendation_algorithm',
            'Media', 'QSpacerItem', 'QSizePolicy', 'QApplication', 'requests', 'csv', 'graph_classes', 'filter_movies',
            'anime_filter'
        ],
        # the names (strs) of imported modules
        'allowed-io': [
            'extract_movies_file',
            'extract_images_file',
            'modified_get_recommendations',
            'MainWindow.on_submit',
            'build_keyword_graph_from_file'
        ],
        # the names (strs) of functions that call print/open/input
        'disable': ['E0611', 'E9992', 'E9997', 'R0902', 'W0123'],
        # Need E0611 and R0902 especially because of instance attributes
        'max-line-length': 120
    })


sys.exit(app.exec())
