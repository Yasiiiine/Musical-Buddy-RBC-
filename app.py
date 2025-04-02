from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QLabel
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QMovie

from screens import Screen

from Modules.metronome.ui import MetronomeScreen
from Modules.tuner.ui import renderArea

#from Modules.Template2.ui import renderArea
from Modules.enregistrement.ui import Module3Screen
from Modules.Template4.ui import Module4Screen
from Modules.transcripteurMIDI.ui import Module5Screen
from Modules.Template6.ui import Module6Screen

import config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(128, 160, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        self.stack = QStackedWidget()
        # Create overlay MovieLabel
        self.movie_label = QLabel(self)
        self.movie_label.setGeometry(0, 0, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.movie_label.setAlignment(Qt.AlignCenter)
        self.movie_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # Let clicks go through
        self.movie_label.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # Transparent background

        self.movie = QMovie("Assets/TransiLM.gif")
        self.movie.setScaledSize(QSize(480, 320))
        self.movie_label.setMovie(self.movie)
        self.movie_label.hide()

        self.setCentralWidget(self.stack)

        self.screens = []

        for i in range(7):
            if i == 0:
                screen = Screen(i)
            elif i == 1:
                screen = MetronomeScreen()
            elif i == 2:
                screen = renderArea()
            elif i == 3:
                screen = Module3Screen()
            elif i == 4:
                screen = Module4Screen()
            elif i == 5:
                screen = Module5Screen()
            elif i == 6:
                screen = Module6Screen()
            else:
                screen = Screen(i, text=f"Module {i}", color="#dddddd")

            self.screens.append(screen)
            self.stack.addWidget(screen)

        self.current_index = 0
        self.stack.setCurrentIndex(self.current_index)
        self.setFocusPolicy(Qt.StrongFocus)

        # Démarre le premier écran si nécessaire
        current_screen = self.screens[self.current_index]
        if hasattr(current_screen, "start"):
            current_screen.start()

    def keyPressEvent(self, event):
        previous_screen = self.screens[self.current_index]

        if event.key() == Qt.Key_D:
            self.current_index = (self.current_index + 1) % 7
        elif event.key() == Qt.Key_Q:
            self.current_index = (self.current_index - 1) % 7
        elif event.key() == Qt.Key_Space:
            self.current_index = 0

        # Show the bootup animation
        self.movie_label.show()
        self.movie.start()
        QTimer.singleShot(3000, self.movie_label.hide)  # hide after 3 seconds

        next_screen = self.screens[self.current_index]

        if hasattr(previous_screen, "stop"):
            previous_screen.stop()

        if hasattr(next_screen, "start"):
            next_screen.start()

        self.stack.setCurrentIndex(self.current_index)
