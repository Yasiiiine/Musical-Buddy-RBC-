from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from screens import Screen

from Modules.metronome.ui import MetronomeScreen
<<<<<<< Updated upstream
from Modules.tuner.ui import renderArea
=======
from Modules.Template2.ui import renderArea
>>>>>>> Stashed changes
from Modules.enregistrement.ui import Module3Screen
from Modules.Template4.ui import Module4Screen
from Modules.Template5.ui import Module5Screen
from Modules.Template6.ui import Module6Screen

import config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(128, 160, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.screens = []

        for i in range(7):
            if i == 0:
                screen = Screen(i, text="Home", color="#e0e0e0")
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

        next_screen = self.screens[self.current_index]

        if hasattr(previous_screen, "stop"):
            previous_screen.stop()

        if hasattr(next_screen, "start"):
            next_screen.start()

        self.stack.setCurrentIndex(self.current_index)
