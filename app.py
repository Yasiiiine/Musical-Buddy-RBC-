from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt
from screens import Screen
import config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(128, 160, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # Gestionnaire d'écrans
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Ajout des écrans de 0 à 5
        self.screens = [Screen(str(i)) for i in range(7)]
        for screen in self.screens:
            self.stack.addWidget(screen)

        self.current_index = 0
        self.stack.setCurrentIndex(self.current_index)

        # Forcer le focus clavier sur la fenêtre
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        """Gestion des touches pour naviguer entre les écrans"""
        if event.key() == Qt.Key_D:  # Aller à l'écran suivant
            self.current_index = (self.current_index + 1) % 7
        elif event.key() == Qt.Key_Q:  # Aller à l'écran précédent
            self.current_index = (self.current_index - 1) % 7
        elif event.key() == Qt.Key_Space:  # Retour à l'écran principal
            self.current_index = 0

        print(f"Changement vers l'écran : {self.current_index}")  # Debugging
        self.stack.setCurrentIndex(self.current_index)  # Mettre à jour l'écran affiché
