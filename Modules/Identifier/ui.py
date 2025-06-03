# ui.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox, QSizePolicy, QScrollArea, QHBoxLayout, QApplication
from PyQt5.QtCore import Qt, QEvent, QTimer
import os
from core.styles import retro_label_font, bpm_label_style
import Modules.Identifier.config as cfg
from Modules.Identifier.logic import identify_song
from Modules.Streamer.logic import MusicPlayer

class IdentifierScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {cfg.MODULE_COLOR};")
        self.label = QLabel(cfg.MODULE_LABEL)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(retro_label_font(32))
        self.label.setStyleSheet(bpm_label_style())

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setFont(retro_label_font(18))

        # Instanciation du MusicPlayer du module Streamer
        self.music_player = MusicPlayer()
        self._playback_connected = False
        
        # Button pour jouer le morceau identifié - masqué par défaut
        self.play_button = QPushButton("Écouter ce morceau")
        self.play_button.setFont(retro_label_font(18))
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: #5d8271;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #406356;
            }
        """)
        self.play_button.clicked.connect(self.play_identified_song)
        self.play_button.hide()  # Masqué jusqu'à ce qu'une chanson soit identifiée
        
        # Pour stocker les infos de la chanson identifiée
        self.current_song = None

        self.selected_index = 0
        self.items_per_page = 3  # Pour la hauteur du scroll area

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.recordings_dir = os.path.join(base_dir, '..', '..','recordingstestm')
        self.recordings = [f for f in os.listdir(self.recordings_dir) if f.lower().endswith(('.mp3', '.wav', '.m4a', '.aac', '.flac'))]
        self.recording_buttons = []

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        layout.addWidget(self.label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.recording_buttons_layout = QVBoxLayout()
        self.recording_buttons_layout.setSpacing(10)
        scroll_content.setLayout(self.recording_buttons_layout)

        scroll_area.setWidget(scroll_content)
        scroll_area.setFixedHeight(self.items_per_page * 50 + 10)
        scroll_area.setFixedWidth(550)
        layout.addWidget(scroll_area, alignment=Qt.AlignHCenter)

        layout.addWidget(self.result_label)
        layout.addWidget(self.play_button, alignment=Qt.AlignCenter)  # Ajout du bouton de lecture
        layout.addStretch(1)
        self.setLayout(layout)

        self.update_recording_buttons()

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def shorten_text(self, text, max_length=40):
        if len(text) <= max_length:
            return text
        else:
            return text[:max_length-3] + "..."

    def update_recording_buttons(self):
        for i in reversed(range(self.recording_buttons_layout.count())):
            container_widget = self.recording_buttons_layout.itemAt(i).widget()
            if container_widget is not None:
                container_widget.deleteLater()
        self.recording_buttons.clear()
        for i, recording_name in enumerate(self.recordings):
            short_name = self.shorten_text(recording_name)
            button = QPushButton(short_name)
            button.setFixedWidth(500)
            button.setMinimumHeight(30)
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            button.clicked.connect(lambda checked, r=recording_name: self.identify_recording(r))
            button.installEventFilter(self)
            self.recording_buttons.append(button)
            if i == self.selected_index:
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 14px;
                        padding: 4px 10px;
                        background-color: #555555;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        text-align: left;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 14px;
                        padding: 4px 10px;
                        background-color: #5d8271;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        text-align: left;
                    }
                """)
            container = QWidget()
            container_layout = QHBoxLayout()
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.addStretch()
            container_layout.addWidget(button)
            container_layout.addStretch()
            container.setLayout(container_layout)
            self.recording_buttons_layout.addWidget(container)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Enter and isinstance(source, QPushButton) and source in self.recording_buttons:
            hovered_index = self.recording_buttons.index(source)
            if self.selected_index != hovered_index:
                if 0 <= self.selected_index < len(self.recording_buttons):
                    prev_button = self.recording_buttons[self.selected_index]
                    prev_button.setStyleSheet("""
                        QPushButton {
                            font-size: 14px;
                            padding: 4px 10px;
                            background-color: #5d8271;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            text-align: left;
                        }
                    """)
                source.setStyleSheet("""
                    QPushButton {
                        font-size: 14px;
                        padding: 4px 10px;
                        background-color: #555555;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        text-align: left;
                    }
                """)
                self.selected_index = hovered_index
        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_recording_buttons()
        elif event.key() == Qt.Key_Down:
            if self.selected_index < len(self.recordings) - 1:
                self.selected_index += 1
                self.update_recording_buttons()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if 0 <= self.selected_index < len(self.recordings):
                self.identify_recording(self.recordings[self.selected_index])
        else:
            super().keyPressEvent(event)

    def identify_recording(self, filename):
        # Arrêter toute lecture en cours
        if self.music_player.is_playing():
            self.music_player.stop()
        
        file_path = os.path.join(self.recordings_dir, filename)
        self.result_label.setText("Identification en cours...")
        self.play_button.hide()  # Cacher le bouton pendant l'identification
        QApplication.processEvents()
        
        result = identify_song(file_path)
        
        if 'error' in result:
            QMessageBox.warning(self, "Erreur", result['error'])
            self.result_label.setText("")
            self.current_song = None
        else:
            self.result_label.setText(f"Titre : {result['title']}\nArtiste : {result['artist']}\nAlbum : {result['album']}\nSpotify : {result['spotify_url']}\nApple Music : {result['apple_music_url']}")
              # Stocker les infos de la chanson et afficher le bouton de lecture
            self.current_song = f"{result['artist']} - {result['title']}"
            self.play_button.setText(f"Écouter \"{self.shorten_text(self.current_song, 35)}\"")
            self.play_button.show()
    
    def play_identified_song(self):
        if not self.current_song:
            return
          # Si la lecture est déjà en cours, arrêter le morceau
        if self.music_player.is_playing():
            self.music_player.stop()
            self.play_button.setText(f"Écouter \"{self.shorten_text(self.current_song, 35)}\"")
            return
            
        # Changer le bouton pendant la recherche
        self.play_button.setText("Recherche en cours...")
        self.play_button.setEnabled(False)
        QApplication.processEvents()
            
        # Utiliser le music_player du module Streamer pour jouer la chanson
        self.music_player.play(self.current_song)
        
        # Attendre un petit moment pour que la lecture démarre
        QTimer.singleShot(1500, self.update_play_button_state)
        
    def update_play_button_state(self):
        """Met à jour l'état du bouton selon l'état de lecture actuel"""
        self.play_button.setEnabled(True)
        
        if self.music_player.is_playing():
            self.play_button.setText("Arrêter la lecture")
            # S'assurer qu'on surveille la fin de la lecture
            if not hasattr(self, "_playback_connected") or not self._playback_connected:
                self.music_player.timer.timeout.connect(self.check_playback_status)
                self._playback_connected = True
        else:
            song_short = self.shorten_text(self.current_song, 30)
            self.play_button.setText(f"Réessayer avec \"{song_short}\"")
            # Afficher un message explicatif
            QMessageBox.information(self, "Lecture", 
                                   f"Impossible de lire '{self.current_song}'. Vérifiez votre connexion internet ou essayez avec un autre titre.")
                
    def check_playback_status(self):
        """Appelé périodiquement pour vérifier si la lecture est terminée"""
        if not self.music_player.is_playing():
            self.play_button.setText(f"Écouter \"{self.shorten_text(self.current_song, 35)}\"")
            # Déconnecter le signal pour éviter les appels multiples
            if hasattr(self, "_playback_connected") and self._playback_connected:
                try:
                    self.music_player.timer.timeout.disconnect(self.check_playback_status)
                except TypeError:  # Au cas où la déconnexion échoue
                    pass
                self._playback_connected = False
