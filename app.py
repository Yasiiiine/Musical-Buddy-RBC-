from PyQt5.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, QSize, QUrl, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QMovie, QPixmap, QIcon
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
from Modules.Identifier.ui import IdentifierScreen
from Modules.Parametres.ui import Module7Screen

class BootupScreen(QWidget):
    def __init__(self, on_finished_callback=None):
        super().__init__()

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;")
        self.label.setScaledContents(True)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.movie = QMovie(asset_path("BootupLM.gif"))
        self.label.setMovie(self.movie)
        self.movie.frameChanged.connect(self.ensure_movie_size_once)
        self._movie_scaled_applied = False

        self._on_finished_callback = on_finished_callback

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

        # Force resize logic
        self.resizeEvent(None)

        # Mark as applied to avoid future redundant resizes
        self._movie_scaled_applied = True


    def resizeEvent(self, event):
        super().resizeEvent(event)

        window_size = self.size()
        original_size = self.movie.scaledSize()  # Use set size or fallback

        if original_size.isEmpty():
            original_size = QSize(1024, 600)  # Fallback size if empty

        scaled_size = original_size.scaled(window_size, Qt.KeepAspectRatio)
        self.movie.setScaledSize(scaled_size)
        self.label.resize(scaled_size)
        self.label.move(
            (self.width() - scaled_size.width()) // 2,
            (self.height() - scaled_size.height()) // 2
        )
    
    def mousePressEvent(self, event):
        if self._on_finished_callback:
            self._on_finished_callback()

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
        self.setGeometry(600, 1024, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # Create a container widget and layout
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create your stack as before
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self.screens = []
        self.screen_wrappers = []

        # Bootup screen
        self.bootup_screen = BootupScreen(on_finished_callback=self.start_first_screen)
        self.stack.addWidget(self.bootup_screen)

        # Transition screen with BGLM
        self.transition_screen = TransitionScreen()
        self.stack.addWidget(self.transition_screen)

        # All module screens
        modules = [
            Screen(0),
            MetronomeScreen(),
            renderArea(),
            Record(),
            Module4Screen(),#Lecture
            Module5Screen(),#Transcription MIDI
            IdentifierScreen(),#Recommendation
            Module7Screen()
        ]

        for screen in modules:
            wrapper = wrap_widget(screen)
            self.screens.append(screen)
            self.screen_wrappers.append(wrapper)
            self.stack.addWidget(wrapper)

        self.current_index = 2  # First real screen index

        self.background_label = QLabel(self)
        self.background_label.setPixmap(QPixmap(asset_path(config.bg_light_image)))
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
        self.movie.setScaledSize(QSize(1024, 600))
        self.movie.jumpToFrame(0)  # Preload first frame
        self.movie_label.resize(self.movie.scaledSize())
        self.movie_label.setMovie(self.movie)
        self.movie_label.hide()
        self.center_movie_label()


        # Woosh sound
        self.transition_sound = QSoundEffect()
        self.transition_sound.setSource(QUrl.fromLocalFile(os.path.join("Assets", "woosh.wav")))
        self.transition_sound.setVolume(0.8)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(20)

        # Navigation buttons with PNG icons
        self.left_button = QPushButton()
        self.right_button = QPushButton()
        self.left_button.setIcon(QIcon("Assets/left.png"))
        self.right_button.setIcon(QIcon("Assets/right.png"))
        self.left_button.setIconSize(QSize(80, 80))  # Adjust size as needed
        self.right_button.setIconSize(QSize(80, 80))
        self.left_button.setStyleSheet("background: transparent; border: none;")
        self.right_button.setStyleSheet("background: transparent; border: none;")


        self.left_button.clicked.connect(self.go_left)
        self.right_button.clicked.connect(self.go_right)

        # Overlay navigation buttons
        self.left_button.setParent(self)
        self.right_button.setParent(self)
        self.left_button.raise_()
        self.right_button.raise_()
        self.left_button.show()
        self.right_button.show()
        self.update_nav_buttons_position()


        nav_layout.addWidget(self.left_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.right_button)

        self.setCentralWidget(container)
        self.set_background()
        
    def set_background(self):
        """
        Switches self.background_label’s pixmap to light or dark,
        based on config.is_dark_mode. Must be called whenever we toggle
        theme or when the window is first shown.
        """
        # Choose which filename to load
        if config.is_dark_mode:
            chosen = config.bg_dark_image
        else:
            chosen = config.bg_light_image

        # Load & apply it
        px = QPixmap(asset_path(chosen))
        self.background_label.setPixmap(px)

        # Make sure the label fills the entire window
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(self.rect())

        # Ensure it is positioned “behind” all other widgets
        self.background_label.lower()
        self.background_label.show()  # Always show once for any mode
        try:
            self.transition_screen.set_background()
        except AttributeError:
            # If transition_screen does not exist (unlikely), just ignore.
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.background_label.setGeometry(self.rect())
        self.center_movie_label()
        self.update_nav_buttons_position()

    def update_nav_buttons_position(self):
        btn_size = self.left_button.iconSize()
        y = (self.height() - btn_size.height()) // 2
        margin = 40  # distance from the edge, adjust as needed
        self.left_button.setGeometry(margin, y, btn_size.width(), btn_size.height())
        self.right_button.setGeometry(self.width() - btn_size.width() - margin, y, btn_size.width(), btn_size.height())

    def go_left(self):
        # Simulate pressing Q (previous screen)
        prev_screen = self.screens[self.current_index - 2]
        next_index = (self.current_index - 2 - 1) % len(self.screens)
        if hasattr(prev_screen, "stop"):
            prev_screen.stop()
        self.fade_widget(self.screen_wrappers[self.current_index - 2], 1, 0, 250,
                         on_finished=lambda: self.start_transition(next_index + 2))

    def go_right(self):
        # Simulate pressing D (next screen)
        prev_screen = self.screens[self.current_index - 2]
        next_index = (self.current_index - 2 + 1) % len(self.screens)
        if hasattr(prev_screen, "stop"):
            prev_screen.stop()
        self.fade_widget(self.screen_wrappers[self.current_index - 2], 1, 0, 250,
                         on_finished=lambda: self.start_transition(next_index + 2))

    def start_first_screen(self):
        self.background_label.show()  # Show the background now
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

        # Fade out current screen wrapper
        self.fade_widget(self.screen_wrappers[self.current_index - 2], 1, 0, 250,
                         on_finished=lambda: self.start_transition(next_index + 2))

    def start_transition(self, next_index):
        # Show and start the GIF immediately
        self.movie.jumpToFrame(0)
        self.movie_label.show()
        self.movie_label.raise_()
        self.movie.start()
        self.movie_label.repaint()  # Force immediate draw

        # Play sound as GIF starts
        self.transition_sound.play()

        # Now switch to the transition screen after a short delay
        QTimer.singleShot(50, lambda: self.stack.setCurrentWidget(self.transition_screen))
        QTimer.singleShot(200, lambda: self.switch_and_fade_in(next_index))
        self.left_button.raise_()
        self.right_button.raise_()
        self.movie_label.raise_()


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
        self.left_button.raise_()
        self.right_button.raise_()
        self.movie_label.raise_()

    def fade_widget(self, widget, start, end, duration, on_finished=None):
        effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        widget.setVisible(True)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setEasingCurve(QEasingCurve.InOutQuad)

        self._fade_anim = anim  # Keep reference alive
        if on_finished:
            anim.finished.connect(on_finished)
        anim.start()

    def center_movie_label(self):
        movie_size = self.movie.scaledSize()
        x = (self.width() - movie_size.width()) // 2
        y = (self.height() - movie_size.height()) // 2
        self.movie_label.move(x, y)
