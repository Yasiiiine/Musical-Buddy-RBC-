from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QMovie
from screens import Screen, TransitionScreen

from Modules.metronome.ui import MetronomeScreen
from Modules.tuner.ui import renderArea
from Modules.enregistrement.ui import Module3Screen
from Modules.Template4.ui import Module4Screen
from Modules.transcripteurMIDI.ui import Module5Screen
from Modules.Template6.ui import Module6Screen


import config

# --- Fullscreen Bootup screen as a stacked widget ---
from PyQt5.QtWidgets import QWidget, QLabel


class BootupScreen(QWidget):
    def __init__(self, on_finished_callback=None):
        super().__init__()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;")

        self.movie = QMovie("Assets/BootupLM.gif")
        self.movie.setSpeed(100)
        self.movie.setScaledSize(QSize(480, 320))
        self.label.setMovie(self.movie)

        self.label.resize(self.movie.scaledSize())
        self.resize(self.movie.scaledSize())
        self.center_label()

        if on_finished_callback:
            duration = self.movie.frameCount() * self.movie.nextFrameDelay()
            QTimer.singleShot(duration, on_finished_callback)

        self.movie.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.center_label()

    def center_label(self):
        movie_size = self.movie.scaledSize()
        x = (self.width() - movie_size.width()) // 2
        y = (self.height() - movie_size.height()) // 2
        self.label.move(x, y)


# --- Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(128, 160, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.screens = []

        # Add the bootup screen first
        self.bootup_screen = BootupScreen(on_finished_callback=self.start_first_screen)
        self.stack.addWidget(self.bootup_screen)

        # Add transition screen (index 1)
        self.transition_screen = TransitionScreen()
        self.stack.addWidget(self.transition_screen)

        # Add all module screens (index 2 to 8)
        modules = [
            Screen(0),
            MetronomeScreen(),
            renderArea(),
            Module3Screen(),
            Module4Screen(),
            Module5Screen(),
            Module6Screen(),
        ]

        for screen in modules:
            self.screens.append(screen)
            self.stack.addWidget(screen)

        self.current_index = 2  # First real screen is at index 2 in stack
        self.setFocusPolicy(Qt.StrongFocus)

        # Create overlay transition GIF
        self.movie_label = QLabel(self)
        self.movie_label.setAlignment(Qt.AlignCenter)
        self.movie_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.movie_label.setStyleSheet("background-color: rgba(0, 0, 0, 0);")

        self.movie = QMovie("Assets/TransiLM.gif")
        self.movie.setSpeed(175)
        self.movie.setScaledSize(QSize(480, 320))
        self.movie_label.resize(self.movie.scaledSize())
        self.movie_label.setMovie(self.movie)
        self.movie_label.hide()
        self.center_movie_label()

    def start_first_screen(self):
        self.stack.setCurrentIndex(self.current_index)
        first_screen = self.screens[0]
        if hasattr(first_screen, "start"):
            first_screen.start()

    def keyPressEvent(self, event):
        previous_screen = self.screens[self.current_index - 2]

        if event.key() == Qt.Key_D:
            next_index = (self.current_index - 2 + 1) % len(self.screens)
        elif event.key() == Qt.Key_Q:
            next_index = (self.current_index - 2 - 1) % len(self.screens)
        elif event.key() == Qt.Key_Space:
            next_index = 0
        else:
            return

        if hasattr(previous_screen, "stop"):
            previous_screen.stop()

        # Play transition animation
        self.movie.start()
        self.movie.jumpToFrame(0)
        self.movie_label.raise_()
        self.movie_label.show()

        # Show transition screen briefly
        QTimer.singleShot(300, lambda: self.stack.setCurrentWidget(self.transition_screen))

        # Switch to target screen
        QTimer.singleShot(600, lambda: self.switch_to_screen(next_index + 2))

    def switch_to_screen(self, index):
        self.current_index = index
        next_screen = self.screens[self.current_index - 2]
        if hasattr(next_screen, "start"):
            next_screen.start()
        self.stack.setCurrentIndex(self.current_index)

    def center_movie_label(self):
        movie_size = self.movie.scaledSize()
        x = (self.width() - movie_size.width()) // 2
        y = (self.height() - movie_size.height()) // 2
        self.movie_label.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.center_movie_label()
