"""test qt"""
import json

import PyQt6

import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QCompleter,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)


class OnOffWidget(QWidget):
    """deez"""
    def __init__(self, name):
        super(OnOffWidget, self).__init__()

        self.name = name  # Name of widget used for searching.
        self.label = QLabel(self.name)
        self.remove_button = QPushButton('X')

        self.hbox = QHBoxLayout()  # A horizontal layout to encapsulate the above
        self.hbox.addWidget(self.label)  # Add the label to the layout
        self.hbox.addWidget(self.remove_button)
        self.setLayout(self.hbox)


def extract_movies_file(filename: str) -> set:
    """extract movies file"""
    names = set()

    with open(filename, 'r') as f:
        string = f.read()
        for line in json.loads(string):
            names.add(line['title'])

    return names


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    """
        we
    """
    searchbar: QLineEdit

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Anime Recommendation System")
        self.controls = QWidget()
        self.controlsLayout = QVBoxLayout()
        self.searchbar = QLineEdit()
        self.button_push = QPushButton()

        layout = QVBoxLayout()
        widgets = [
            QCheckBox,
            QLabel,
        ]

        self.widgets = []

        movie_names = extract_movies_file('datasets/filtered/final_movies.json')

        for name in movie_names:
            item = OnOffWidget(name)
            self.controlsLayout.addWidget(item)
            self.widgets.append(item)

        spacer = QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.controlsLayout.addItem(spacer)
        self.controls.setLayout(self.controlsLayout)

        widget = QLabel("Enter a list of movies you've watched below!")
        widget.setFont(QFont('Verdana', 20))
        widget.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(widget)

        layout.addWidget(self.searchbar)

        for w in widgets:
            if w is not QCompleter:
                layout.addWidget(w())

        layout.addWidget(self.button_push)

        widget = QWidget()
        widget.setLayout(layout)

        # Adding Completer.
        self.completer = QCompleter(movie_names)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.searchbar.setCompleter(self.completer)

        # Set the central widget of the Window. Widget will expand
        # to take up all the space in the window by default.
        self.setCentralWidget(widget)


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
