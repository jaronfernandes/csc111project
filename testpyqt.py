"""test qt

jaiz if you see this im sorry for the code being so messy and undocumented lol

i will fix later
"""
from __future__ import annotations

import json
import random
import os

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6 import QtCore


BACKGROUND_IMAGE = f"imgs/{random.choice(os.listdir('imgs'))}"  # Picks a random one at the start


def extract_movies_file(filename: str) -> set:
    """extract movies file"""
    names = set()

    with open(filename, 'r') as f:
        string = f.read()
        for line in json.loads(string):
            names.add(line['title'])

    return names


class MovieWidget(QWidget):
    """Widget for each movie in the dropdown."""
    movie_name: str
    label: QLabel
    close_button: QPushButton
    layout: QHBoxLayout
    parent: MainWindow

    def __init__(self, movie_name: str, parent: MainWindow):
        """Initializer"""
        super(MovieWidget, self).__init__()
        self.parent = parent

        # self.setMaximumHeight(50)
        self.movie_name = movie_name
        self.label = QLabel(self.movie_name, self)
        self.close_button = QPushButton('X', self)
        self.close_button.setFixedSize(QtCore.QSize(40, 40))
        self.close_button.setFont(QFont('Verdana', 30))

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.label)
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
    scroll: QScrollArea
    searchbar: QLineEdit
    movies: set

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

        group_box.setLayout(self.form_layout)

        # Scroll Area Properties.
        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(group_box)

        # Creating the container
        container = QWidget()
        container_layout = QVBoxLayout()
        row = QFormLayout()
        row.addRow(self.searchbar, self.add_movie_button)
        container_layout.addLayout(row)
        thing = QVBoxLayout()

        self.scroll.setLayout(thing)
        container_layout.addWidget(self.scroll)

        # for movie in self.movies:
        #     container_layout.addWidget(movie)

        container.setLayout(container_layout)
        self.setCentralWidget(container)

        self.add_movie_button.clicked.connect(self.on_movie_added)

    def on_movie_added(self) -> None:
        """Button for when movies are added"""
        text = self.searchbar.text()
        if text in self.movies and text not in self.added_movies:
            self.form_layout.addRow(MovieWidget(text, self))
            self.added_movies.add(text)
            print(self.added_movies)


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
