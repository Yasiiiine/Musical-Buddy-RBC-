# AudioSettingsManager.py
import sounddevice as sd

class AudioSettingsManager:
    selected_input_device_index = None

    @classmethod
    def list_input_devices(cls):
        return [device['name'] for device in sd.query_devices() if device['max_input_channels'] > 0]

    @classmethod
    def set_input_device(cls, index):
        cls.selected_input_device_index = index

    @classmethod
    def get_input_device(cls):
        return cls.selected_input_device_index
