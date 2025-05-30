from PyQt5.QtWidgets import QApplication
from app import MainWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    #window.showFullScreen()
    sys.exit(app.exec_())
