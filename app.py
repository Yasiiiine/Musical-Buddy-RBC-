from PyQt5.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
)
from PyQt5.QtCore import Qt, QTimer, QSize, QUrl, QPropertyAnimation, QEasingCurve, QEvent
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QSwipeGesture
from PyQt5.QtMultimedia import QSoundEffect
import os
import config
from core.utils import asset_path
from screens import Screen, TransitionScreen
from Modules.metronome.ui import MetronomeScreen
from Modules.tuner.ui import renderArea
from Modules.enregistrement.ui import Record
from Modules.player.ui import Module4Screen
from Modules.transcripteurMIDI.ui import Module5Screen
from Modules.Template6.ui import Module6Screen
from Modules.Parametres.ui import Module7Screen


class BootupScreen(QWidget):
    def __init__(self, on_finished_callback=None):
        super().__init__()

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;")
        self.label.setScaledContents(True)

        self.movie = QMovie(asset_path("BootupLM.gif"))
        self.label.setMovie(self.movie)
        self.movie.frameChanged.connect(self.ensure_movie_size_once)
        self._movie_scaled_applied = False

        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(asset_path("Bootup.wav")))
        self.sound.setVolume(0.8)

        self.movie.start()
        self.sound.play()

        if on_finished_callback:
            duration = self.movie.frameCount() * self.movie.nextFrameDelay()
            QTimer.singleShot(duration, on_finished_callback)

    def ensure_movie_size_once(self, frameNumber):
        if self._movie_scaled_applied:
            return
        self.resizeEvent(None)
        self._movie_scaled_applied = True

    def resizeEvent(self, event):
        super().resizeEvent(event)
        window_size = self.size()
        original_size = self.movie.scaledSize()
        if original_size.isEmpty():
            original_size = QSize(480, 320)
        scaled_size = original_size.scaled(window_size, Qt.KeepAspectRatio)
        self.movie.setScaledSize(scaled_size)
        self.label.resize(scaled_size)
        self.label.move(
            (self.width() - scaled_size.width()) // 2,
            (self.height() - scaled_size.height()) // 2
        )


def wrap_widget(widget):
    wrapper = QWidget()
    layout = QVBoxLayout(wrapper)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(widget)
    return wrapper


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(320, 480, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.screens = []
        self.screen_wrappers = []

        # Bootup screen
        self.bootup_screen = BootupScreen(on_finished_callback=self.start_first_screen)
        self.stack.addWidget(self.bootup_screen)

        # Transition screen
        self.transition_screen = TransitionScreen()
        self.stack.addWidget(self.transition_screen)

        # All module screens
        modules = [
            Screen(0),
            MetronomeScreen(),
            renderArea(),
            Record(),
            Module4Screen(),
            Module5Screen(),
            Module6Screen(),
            Module7Screen()
        ]

        for screen in modules:
            wrapper = wrap_widget(screen)
            self.screens.append(screen)
            self.screen_wrappers.append(wrapper)
            self.stack.addWidget(wrapper)

        self.current_index = 2  # First real screen index

        # Background image
        self.background_label = QLabel(self)
        self.background_label.setPixmap(QPixmap(asset_path("BGLM.png")))
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(self.rect())
        self.background_label.lower()
        self.background_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.background_label.hide()

        # Transition GIF
        self.movie_label = QLabel(self)
        self.movie_label.setAlignment(Qt.AlignCenter)
        self.movie_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.movie_label.setStyleSheet("background-color: transparent;")

        self.movie = QMovie("Assets/TransiLM.gif")
        self.movie.setSpeed(175)
        self.movie.setScaledSize(QSize(480, 320))
        self.movie.jumpToFrame(0)
        self.movie_label.resize(self.movie.scaledSize())
        self.movie_label.setMovie(self.movie)
        self.movie_label.hide()
        self.center_movie_label()

        # Woosh sound
        self.transition_sound = QSoundEffect()
        self.transition_sound.setSource(QUrl.fromLocalFile(os.path.join("Assets", "woosh.wav")))
        self.transition_sound.setVolume(0.8)

        # Enable swipe gestures
        self.grabGesture(Qt.SwipeGesture)

    def start_first_screen(self):
        self.background_label.show()
        self.stack.setCurrentIndex(self.current_index)
        screen = self.screens[0]
        if hasattr(screen, "start"):
            screen.start()

    def keyPressEvent(self, event):
        prev_screen = self.screens[self.current_index - 2]
        if event.key() == Qt.Key_D:
            next_index = (self.current_index - 2 + 1) % len(self.screens)
        elif event.key() == Qt.Key_Q:
            next_index = (self.current_index - 2 - 1) % len(self.screens)
        elif event.key() == Qt.Key_Space:
            next_index = 0
        else:
            return

        if hasattr(prev_screen, "stop"):
            prev_screen.stop()

        self.fade_widget(self.screen_wrappers[self.current_index - 2], 1, 0, 250,
                         on_finished=lambda: self.start_transition(next_index + 2))

    def event(self, event):
        if event.type() == QEvent.Gesture:
            return self.handle_gesture(event)
        return super().event(event)

    def handle_gesture(self, event):
        gesture = event.gesture(Qt.SwipeGesture)
        if gesture:
            if gesture.state() == Qt.GestureFinished:
                if gesture.horizontalDirection() == QSwipeGesture.Left:
                    self.navigate_to_next_screen()
                elif gesture.horizontalDirection() == QSwipeGesture.Right:
                    self.navigate_to_previous_screen()
            return True
        return False

    def navigate_to_next_screen(self):
        next_index = (self.current_index - 2 + 1) % len(self.screens)
        self.start_transition(next_index + 2)

    def navigate_to_previous_screen(self):
        prev_index = (self.current_index - 2 - 1) % len(self.screens)
        self.start_transition(prev_index + 2)

    def start_transition(self, next_index):
        self.movie.jumpToFrame(0)
        self.movie_label.show()
        self.movie_label.raise_()
        self.movie.start()
        self.movie_label.repaint()

        self.transition_sound.play()

        QTimer.singleShot(50, lambda: self.stack.setCurrentWidget(self.transition_screen))
        QTimer.singleShot(200, lambda: self.switch_and_fade_in(next_index))

    def switch_and_fade_in(self, index):
        self.current_index = index
        screen = self.screens[self.current_index - 2]
        wrapper = self.screen_wrappers[self.current_index - 2]

        self.stack.setCurrentWidget(wrapper)
        if hasattr(screen, "start"):
            screen.start()

        wrapper.setGraphicsEffect(None)
        self.fade_widget(wrapper, 0, 1, 300)
        QTimer.singleShot(500, self.movie_label.hide)

    def fade_widget(self, widget, start, end, duration, on_finished=None):
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        widget.setVisible(True)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.InOutQuad)

        self._fade_anim = anim
        if on_finished:
            anim.finished.connect(on_finished)
        anim.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.background_label.setGeometry(self.rect())
        self.center_movie_label()

    def center_movie_label(self):
        movie_size = self.movie.scaledSize()
        x = (self.width() - movie_size.width()) // 2
        y = (self.height() - movie_size.height()) // 2
        self.movie_label.move(x, y)
