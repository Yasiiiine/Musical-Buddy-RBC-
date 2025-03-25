from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
import config

class Screen(QWidget):
    def __init__(self, number, operation=None, label=""):
        super().__init__()
        number = int(number)
        self.operation = operation
        self.label_text = label

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Cas des écrans sans opération : affichage simple comme au départ
        if not operation:
            label_widget = QLabel(str(number))
            label_widget.setAlignment(Qt.AlignCenter)
            label_widget.setStyleSheet("font-size: 50px; font-weight: bold;")
            layout.addWidget(label_widget)

        # Cas des écrans avec opération mathématique
        else:
            # Titre
            title = QLabel(f"Opération : {label}")
            title.setAlignment(Qt.AlignCenter)
            title.setStyleSheet("font-size: 24px; font-weight: bold;")
            layout.addWidget(title)

            # Inputs
            self.input1 = QLineEdit()
            self.input1.setPlaceholderText("Entrer le premier nombre")
            self.input1.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.input1)

            self.input2 = QLineEdit()
            self.input2.setPlaceholderText("Entrer le deuxième nombre")
            self.input2.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.input2)

            # Bouton
            self.button = QPushButton("Calculer")
            self.button.clicked.connect(self.compute)
            layout.addWidget(self.button)

            # Affichage du résultat
            self.result_label = QLabel("Résultat :")
            self.result_label.setAlignment(Qt.AlignCenter)
            self.result_label.setStyleSheet("font-size: 18px;")
            layout.addWidget(self.result_label)

        # Couleur d'arrière-plan
        bg_color = config.BG_COLORS[number]
        self.setStyleSheet(f"background-color: {bg_color};")

        self.setLayout(layout)

    def compute(self):
        try:
            a = float(self.input1.text())
            b = float(self.input2.text())
            result = self.operation(a, b)
            self.result_label.setText(f"Résultat : {result}")
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer deux nombres valides.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur inattendue : {e}")
