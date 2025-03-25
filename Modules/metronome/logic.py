# logic.py

from PyQt5.QtCore import QObject, QTimer, pyqtSignal

class Timer(QObject):
    tick = pyqtSignal()

    def __init__(self, bpm=60):
        super().__init__()
        self.bpm = bpm
        self.timer = QTimer()
        self.timer.timeout.connect(self.emit_tick)
        self.update_interval()
        self.timer.start()

    def emit_tick(self):
        self.tick.emit()

    def update_interval(self):
        interval = int(60000 / self.bpm)  # Intervalle en ms
        self.timer.setInterval(interval)

    def set_bpm(self, bpm):
        self.bpm = max(20, min(300, bpm))
        self.update_interval()
