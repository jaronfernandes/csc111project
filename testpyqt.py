"""test qt

jaiz if you see this im sorry for the code being so messy and undocumented lol

i will fix later
"""
from __future__ import annotations
from typing import Optional

import json
import random
import os

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFont, QPixmap, QFontDatabase
from PyQt6 import QtCore
from Recommedation_algorithm import Media


BACKGROUND_IMAGE = f"imgs/{random.choice(os.listdir('imgs'))}"  # Picks a random one at the start


def extract_movies_file(filename: str) -> dict:
    """extract movies file"""
    names = {}

    with open(filename, 'r') as f:
        string = f.read()
        for line in json.loads(string):
            if 'movie' in filename:
                names[line['title']] = 'Movie'
            elif 'show' in filename:
                names[line['title']] = 'Show'

    return names


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
        super(AnimeWidget, self).__init__()
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
        self.title.move(50, 50)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.description)

        self.box = QGroupBox()
        self.form_layout = QFormLayout()

        self.form_layout.addRow(self.left_button, self.right_button)

        self.box.setLayout(self.form_layout)

        self.layout.addWidget(self.box)

        if image is not None:
            self.image = QPixmap('imgs/samplegradient.jpeg')
            self.title.setPixmap(self.image)

        self.title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.description.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(self.layout)

        self.right_button.clicked.connect(self.switch_animes)
        self.left_button.clicked.connect(self.switch_animes)

    def switch_animes(self, going_left: bool = False) -> None:
        """Button Events to switch the anime recommendation"""
        self.hide()
        if going_left:
            self.left.show()
        else:
            self.right.show()


class MovieWidget(QWidget):
    """Widget for each movie in the dropdown."""
    movie_name: str
    type: QLabel
    label: QLabel
    close_button: QPushButton
    layout: QHBoxLayout
    parent: MainWindow

    def __init__(self, movie_name: str, parent: MainWindow, movie_type: str):
        """Initializer"""
        super(MovieWidget, self).__init__()
        self.parent = parent

        # self.setMaximumHeight(50)
        self.movie_name = movie_name
        self.label = QLabel(self.movie_name, self)
        self.type = QLabel('Type: '+movie_type, self)
        self.close_button = QPushButton('X', self)
        self.close_button.setFixedSize(QtCore.QSize(40, 40))
        self.close_button.setFont(QFont('Verdana', 30))

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.type)
        self.layout.addWidget(self.close_button)
        self.setLayout(self.layout)

        batotn = self.close_button
        batotn.clicked.connect(self.on_clicked)

    def on_clicked(self) -> None:
        """When the button is clicked."""
        self.parent.added_movies.remove(self.movie_name)
        self.layout.removeWidget(self)
        print(self.parent.added_movies)
        # self.destroy()


class MainWindow(QMainWindow):
    """Main window for the application."""
    add_movie_button: QPushButton
    added_movies: set
    completer: QCompleter
    container: QWidget
    container_layout: QVBoxLayout
    form_layout: QFormLayout
    recommendation_layout: QFormLayout
    recommendation_box: QGroupBox
    movies: dict
    scroll: QScrollArea
    searchbar: QLineEdit
    submit_button: QPushButton

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle('Anime Recommendation System')
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.searchbar = QLineEdit()
        self.searchbar.setFixedSize(QtCore.QSize(200, 40))
        self.add_movie_button = QPushButton('Add Movie or Show')
        self.add_movie_button.setFixedSize(QtCore.QSize(200, 40))
        self.form_layout = QFormLayout()
        self.recommendation_layout = QFormLayout()
        self.added_movies = set()

        movie_names = extract_movies_file('datasets/filtered/final_imdb_movies.json')
        movie_names.update(extract_movies_file('datasets/filtered/final_imdb_shows.json'))

        self.movies = movie_names

        # To space the drop-down.
        spacer = QSpacerItem(10, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.container_layout.addItem(spacer)
        self.container.setLayout(self.container_layout)

        # Create the auto-complete
        self.completer = QCompleter(movie_names)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.searchbar.setCompleter(self.completer)

        # Group Box
        group_box = QGroupBox('Movies and Shows Added')
        group_box.setFont(QFont('Verdana', 30))

        group_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)

        anime_box = QGroupBox('Recommended Anime:')
        anime_box.setFont(QFont('Verdana', 30))

        anime_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        anime_box.setLayout(self.recommendation_layout)

        group_box.setLayout(self.form_layout)

        # Scroll Area Properties.
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(group_box)
        self.container_layout.addWidget(anime_box)

        # Creating the container
        container = QWidget()
        container_layout = QVBoxLayout()
        row = QFormLayout()
        row.addRow(self.searchbar, self.add_movie_button)
        container_layout.addLayout(row)
        thing = QVBoxLayout()

        self.scroll.setLayout(thing)
        container_layout.addWidget(self.scroll)
        container_layout.addWidget(anime_box)

        self.recommendation_box = anime_box
        self.recommendation_box.hide()

        self.submit_button = QPushButton('Submit')
        self.submit_button.setFixedSize(QtCore.QSize(200, 40))
        container_layout.addWidget(self.submit_button, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        container.setLayout(container_layout)
        self.setCentralWidget(container)

        self.showMaximized()

        self.add_movie_button.clicked.connect(self.on_movie_added)
        self.submit_button.clicked.connect(self.on_submit)

    def on_movie_added(self) -> None:
        """Button event for when movies are added"""
        text = self.searchbar.text()
        if text in self.movies and text not in self.added_movies:
            self.form_layout.addRow(MovieWidget(text, self, self.movies[text]))
            self.added_movies.add(text)
            print(self.added_movies)

    def on_submit(self) -> None:
        """Button event that triggers recommendation generation
        when the user submits their list of movies/shows.

        Preconditions:
        - The amount of recommended animes returned != 0
        """
        things_to_recommend = self.added_movies
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
                                "ants him to join, but Itadori would rather hang out with the school outcasts in "
                                "the Occult Research Club. One day, the club manages to get their hands on a sealed"
                                " cursed object. Little do they know the terror they\u2019ll unleash when they break"
                                " the seal\u2026'",
                "genre": [
                    "Action",
                    "Horror"
                ]
            }, 'anime'),
            Media({
                "title": "WarfighterXK Anime",
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
            }, 'anime')
        ]
        self.okay = {}
        for i in range(0, len(lst)):
            anime = lst[i]

            if i == 0:
                self.okay[anime.title] = AnimeWidget(anime, self)
                self.recommendation_layout.addRow(self.okay[anime.title])

            # centerPoint = QDesktopWidget().availableGeometry().center()
            # qtRectangle.moveCenter(centerPoint)
            # self.okay[anime.title] = QLabel(anime.title, self)
            # self.okay[anime.title].move(500, 100)
            # self.okay[anime.title].show()

            self.recommendation_layout.addRow(self.okay[anime.title])
            if i + 1 != len(lst):
                self.okay[lst[i + 1].title] = AnimeWidget(lst[i + 1], self)
                self.okay[anime.title].right = self.okay[lst[i + 1].title]
            if i != 0:
                self.okay[anime.title].left = self.okay[lst[i - 1].title]
                self.okay[anime.title].hide()

        self.okay[lst[-1].title].right = self.okay[lst[0].title]
        self.okay[lst[0].title].left = self.okay[lst[-1].title]

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
sys.exit(app.exec())
