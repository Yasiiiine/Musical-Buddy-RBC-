# Fichier spidev.py factice pour contourner l'erreur d'importation
# Ce fichier est une solution temporaire pour permettre l'exécution de l'application sur Windows
# sans le module spidev qui est spécifique à Linux/Raspberry Pi

class SpiDev:
    """Classe factice simulant SpiDev pour les environnements sans support SPI"""
    
    def __init__(self):
        self.max_speed_hz = 0
        self.mode = 0
        print("SpiDev factice initialisé (mode simulation pour Windows)")
    
    def open(self, bus, device):
        """Simule l'ouverture d'une connexion SPI"""
        print(f"[SIMULATION] Ouverture de la connexion SPI bus={bus}, device={device}")
        return self
    
    def xfer2(self, values):
        """Simule un transfert SPI et retourne des valeurs factices"""
        # Pour l'ADC MCP3008, nous retournons généralement des valeurs entre 0 et 1023
        # Cette implémentation retourne simplement 512 (milieu de la plage) pour tous les canaux
        if len(values) >= 3 and values[0] == 1:  # Format standard pour MCP3008
            channel = (values[1] >> 4) & 0x07
            return [0, 0, 512 >> 8, 512 & 0xFF]
        return [0] * len(values)
    
    def close(self):
        """Simule la fermeture d'une connexion SPI"""
        print("[SIMULATION] Fermeture de la connexion SPI")
        return

print("Module spidev factice chargé pour Windows")
