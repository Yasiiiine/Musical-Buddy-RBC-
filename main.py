from PyQt5.QtWidgets import QApplication
from app import MainWindow
import sys
import Modules.Parametres.ui as UiParam
from core.audio_utils import initialize_audio_devices

if __name__ == "__main__":
    initialize_audio_devices()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    #window.showFullScreen()
    sys.exit(app.exec_())
