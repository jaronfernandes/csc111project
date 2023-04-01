"""test qt

jaiz if you see this im sorry for the code being so messy and undocumented lol

i will fix later
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
from Recommedation_algorithm import Media


# Picks a random background image at the start of the program
BACKGROUND_IMAGE = f"imgs/background_images/{random.choice(os.listdir('imgs/background_images'))}"


def extract_movies_file(filename: str) -> dict:
    """extract movies file

    Preconditions:
    - filename is the path of a valid readable JSON file
    """
    names = {}

    with open(filename, 'r') as f:
        string = f.read()
        for line in json.loads(string):
            if 'movie' in filename:
                names[line['title']] = 'Movie'
            elif 'show' in filename:
                names[line['title']] = 'Show'

    return names


def extract_images_file() -> dict[str, str]:
    """Extracting images for animes through the AnimeList.csv dataset.
    Manipulates the invalid image URLs into valid (working) ones
    """
    images = {}

    with open('datasets/raw/AnimeList.csv', 'r') as file:
        reader = csv.reader(file)

        next(reader)

        for row in reader:
            # Loop Invariant:
            assert row[5] == '' or row[5].find('anime/') == 40  # row[5] is not an empty str ==> index is 40

            images[row[1]] = 'https://cdn.myanimelist.net/images/anime/' + row[5][46:]

    return images


class AnimeWidget(QWidget):
    """Widget for each recommended anime."""
    anime_data: Media
    box: QGroupBox
    form_layout: QFormLayout
    full_description: str
    description: QLabel
    image: Optional[QPixmap]
    layout: QVBoxLayout
    left: Optional[AnimeWidget]
    left_button: QPushButton
    parent: MainWindow
    right: Optional[AnimeWidget]
    right_button: QPushButton
    title: QLabel

    def __init__(self, anime_data: Media, parent: MainWindow, image: Optional[str] = None) -> None:
        """Initializer"""
        super().__init__()
        self.parent = parent
        self.anime_data = anime_data
        self.full_description = anime_data.synopsis
        self.description = QLabel(anime_data.synopsis[:200] + '...')
        self.description.setWordWrap(True)
        self.description.setFont(QFont('Verdana', 20))
        self.layout = QVBoxLayout()
        self.title = QLabel(anime_data.title)
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
        spacer2 = QSpacerItem(0, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.layout.addItem(spacer2)  # SPACER IS IMPORTANT FOR MAKING THE < > ARROWS DETACHED!!!
        self.layout.addWidget(self.description)

        self.box = QGroupBox()
        self.form_layout = QFormLayout()

        self.form_layout.addRow(self.left_button, self.right_button)

        self.box.setLayout(self.form_layout)

        # Attempting to find an image (within a try-except in-case internet or image does not exist)
        image = QImage()
        try:
            url = self.parent.movie_images[self.title.text()]
            image.loadFromData(requests.get(url).content)
        except (KeyError, LookupError):
            image = QPixmap('imgs/sadge.jpeg')
        finally:
            self.title.setPixmap(QPixmap(image))
            self.title.setScaledContents(True)
            self.title.setFixedSize(250, 250)

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.layout.addItem(spacer)  # SPACER IS IMPORTANT FOR MAKING THE < > ARROWS DETACHED!!!

        #  self.submit_button.setFixedSize(QtCore.QSize(200, 40))
        # self.layout.addWidget(self.left_button, alignment=Qt.AlignmentFlag.AlignHCenter)

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
        self.left.show()

    def switch_animes_right(self) -> None:
        """Button Events to switch the anime recommendation right through LinkedList"""
        self.hide()
        self.right.show()


class MovieWidget(QWidget):
    """Widget for each movie in the dropdown."""
    movie_name: str
    type: QLabel
    label: QLabel
    close_button: QPushButton
    layout: QHBoxLayout
    parent: MainWindow

    def __init__(self, movie_name: str, parent: MainWindow, movie_type: str) -> None:
        """Initializer"""
        super().__init__()
        self.parent = parent

        # self.setMaximumHeight(50)
        self.movie_name = movie_name
        self.label = QLabel(self.movie_name, self)
        self.type = QLabel('Type: ' + movie_type, self)
        self.close_button = QPushButton('X', self)
        self.close_button.setFixedSize(QtCore.QSize(40, 40))
        self.close_button.setFont(QFont('Verdana', 30))

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.type)
        self.type.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.close_button)
        self.setLayout(self.layout)

        batotn = self.close_button
        batotn.clicked.connect(self.on_clicked)

    def on_clicked(self) -> None:
        """When the button is clicked."""
        self.parent.added_movies.remove(self.movie_name)
        self.layout.removeWidget(self)
        # print(self.parent.added_movies)
        # self.destroy()


class MainWindow(QMainWindow):
    """Main window for the application."""
    add_movie_button: QPushButton
    added_movies: set
    container: QWidget
    container_layout: QVBoxLayout
    form_layout: QFormLayout
    movies: dict
    movie_images: dict[str, str]
    recommended_animes: dict
    recommendation_layout: QFormLayout
    recommendation_box: QGroupBox
    scroll: QScrollArea
    searchbar: QLineEdit
    submit_button: QPushButton

    def __init__(self) -> None:
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
        self.scroll = QScrollArea()
        self.added_movies = set()

        movie_names = extract_movies_file('datasets/filtered/final_imdb_movies.json')
        movie_names.update(extract_movies_file('datasets/filtered/final_imdb_shows.json'))

        self.movies = movie_names
        self.movie_images = extract_images_file()

        self.create_interface()

    def create_interface(self) -> None:
        """Helper method to continue creating the interface."""
        # To space the drop-down.
        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.container_layout.addItem(spacer)
        self.container.setLayout(self.container_layout)

        # Create the auto-complete
        completer = QCompleter(self.movies)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.searchbar.setCompleter(completer)

        # Group Box
        group_box = QGroupBox('Movies and Shows Added')
        group_box.setFont(QFont('Verdana', 30))

        group_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.recommendation_box.setFont(QFont('Verdana', 30))

        self.recommendation_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.recommendation_box.setLayout(self.recommendation_layout)

        group_box.setLayout(self.form_layout)

        # Scroll Area Properties.
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(group_box)
        # self.container_layout.addWidget(anime_box)

        # Creating the container
        container = QWidget()
        container_layout = QVBoxLayout()
        row = QFormLayout()
        row.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)
        row.addRow(self.searchbar, self.add_movie_button)
        container_layout.addLayout(row)
        thing = QVBoxLayout()

        self.scroll.setLayout(thing)
        container_layout.addWidget(self.scroll)
        container_layout.addWidget(self.recommendation_box)

        self.recommendation_box.hide()

        self.submit_button = QPushButton('Submit')
        self.submit_button.setFixedSize(QtCore.QSize(200, 40))
        container_layout.addWidget(self.submit_button, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        container.setLayout(container_layout)
        self.setCentralWidget(container)

        self.showMaximized()
        self.showFullScreen()

        self.add_movie_button.clicked.connect(self.on_movie_added)
        self.submit_button.clicked.connect(self.on_submit)

    def on_movie_added(self) -> None:
        """Button event for when movies are added"""
        text = self.searchbar.text()
        if text in self.movies and text not in self.added_movies:
            self.form_layout.addRow(MovieWidget(text, self, self.movies[text]))
            self.added_movies.add(text)
            # print(self.added_movies)

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
        self.recommendation_box.show()
        lst = [
            Media({
                "title": "Jujutsu Kaisen",
                "release_date": '2020.0',
                "rating": 9.12,
                "keywords": [
                    "Shounen",
                    "Curse",
                    "Exorcists",
                    "Monsters",
                    "School Life",
                    "Supernatural",
                    "Explicit Violence"
                ],
                "plot_summary": "'Although Yuji Itadori looks like your average teenager, "
                                "his immense physical strength is something to behold! Every sports club w"
                                "ants him to join,",
                "genre": [
                    "Action",
                    "Horror"
                ]
            }, 'anime'),
            Media({
                "title": "Shingeki no Kyojin",
                "release_date": '2020.0',
                "rating": 9.12,
                "keywords": [
                    "Shounen",
                    "Curse",
                    "Exorcists",
                    "Monsters",
                    "School Life",
                    "Supernatural",
                    "Explicit Violence"
                ],
                "plot_summary": "'One day, WarfighterXK was born. Then WarfighterXK grew up. The End.'",
                "genre": [
                    "Action",
                    "Horror"
                ]
            }, 'anime'),
            Media({
                "title": "Sword Art Online",
                "release_date": '2069.0',
                "rating": 10,
                "keywords": [
                    "Shounen",
                    "Curse",
                    "Exorcists",
                    "Monsters",
                    "School Life",
                    "Supernatural",
                    "Explicit Violence"
                ],
                "plot_summary": "'Dee was a squirrel who had BIG nuts! His nutsack was SO BIG, that it would drag on "
                                "the ground everywhere he went. Dee had a friend named Sarah who loved nuts, Sarah go "
                                "around town trying to put everyone’s nuts in her mouth. Sarah LOVED how BIG Dee’s nuts"
                                " were, his nuts were her favourite!",
                "genre": [
                    "Action",
                    "Horror"
                ]
            }, 'anime'),
        ]
        for i in range(0, len(lst)):
            anime = lst[i]

            if i == 0:
                self.recommended_animes[anime.title] = AnimeWidget(anime, self)
                self.recommendation_layout.addRow(self.recommended_animes[anime.title])

            # centerPoint = QDesktopWidget().availableGeometry().center()
            # qtRectangle.moveCenter(centerPoint)
            # self.recommended_animes[anime.title] = QLabel(anime.title, self)
            # self.recommended_animes[anime.title].move(500, 100)
            # self.recommended_animes[anime.title].show()

            self.recommendation_layout.addRow(self.recommended_animes[anime.title])
            if i + 1 != len(lst):
                self.recommended_animes[lst[i + 1].title] = AnimeWidget(lst[i + 1], self)
                self.recommended_animes[anime.title].right = self.recommended_animes[lst[i + 1].title]
            if i != 0:
                self.recommended_animes[anime.title].left = self.recommended_animes[lst[i - 1].title]
                self.recommended_animes[anime.title].hide()

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
        font-family: "Verdana", monospace;
        background-image: url({BACKGROUND_IMAGE});
        background-repeat: no-repeat;
        border-image: url({BACKGROUND_IMAGE}) 0 0 0 0 stretch stretch;
        line-height: 20;
        opacity: 0;
    """"""}
    """"""
    QFormLayout {
        border: none;
        background: transparent !important;
        opacity: 0;
    }
    QGroupBox {
        background-color: "white";
        border: none;
        font-family: "Verdana", monospace;
        background: transparent !important;
        color: white;
        font-size: 30px;
        padding: 70px;
        opacity: 0;
    }
    QGroupBox::title {
        border: none;
        font-family: "Verdana", monospace;
        color: white;
        font-size: 30px;
        opacity: 0;
    }
    QFormLayout {
        opacity: 0;
    }
    QPushButton {
        font-size: 16px;
        font-family: "Verdana", monospace;
        background-color: "lightblue";
        border-collapse: separate;
        border-radius: 20%;
        opacity: 0;
    }
    MainWindow::QPushButton {
        font-size: 16px;
        font-family: "Verdana", monospace;
        background-color: "white";
        border-collapse: separate;
        border-radius: 4px;
        opacity: 0;
    }
    QLineEdit {
        background-color: "white";
        font-family: "Verdana", monospace;
        color: "black";
        opacity: 0;
    }
    QLabel {
        font-family: "Verdana", monospace;
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
            'QLineEdit', 'QCompleter', 'QScrollArea', 'QFont', 'QPixmap', 'QtCore', 'Recommedation_algorithm',
            'Media', 'QSpacerItem', 'QSizePolicy', 'QApplication', 'requests', 'csv'
        ],
        # the names (strs) of imported modules
        'allowed-io': ['extract_movies_file', 'extract_images_file'],
        # the names (strs) of functions that call print/open/input
        'disable': ['E0611', 'E9992', 'E9997', 'R0902'],  # Need E0611 and R0902 especially because of instance attribs.
        'max-line-length': 120
    })


sys.exit(app.exec())
