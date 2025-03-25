from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from screens import Screen
from calculs import Calcul
import config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(128, 160, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Dictionnaire des écrans avec opérations
        operation_screens = {
            1: (Calcul.sum, "Addition"),
            2: (Calcul.diff, "Soustraction"),
            3: (Calcul.mult, "Multiplication"),
            4: (Calcul.div, "Division")
        }

        self.screens = []
        for i in range(7):
            if i in operation_screens:
                op, label = operation_screens[i]
                screen = Screen(i, operation=op, label=label)
            else:
                screen = Screen(i)  # écran vierge simple
            self.screens.append(screen)
            self.stack.addWidget(screen)

        self.current_index = 0
        self.stack.setCurrentIndex(self.current_index)
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_D:
            self.current_index = (self.current_index + 1) % 7
        elif event.key() == Qt.Key_Q:
            self.current_index = (self.current_index - 1) % 7
        elif event.key() == Qt.Key_Space:
            self.current_index = 0

        self.stack.setCurrentIndex(self.current_index)
