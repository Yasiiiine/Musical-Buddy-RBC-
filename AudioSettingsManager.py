import sounddevice as sd

class AudioSettingsManager:
    selected_input_device_index = None
    selected_output_device_index = None

    @classmethod
    def list_input_devices(cls):
        return [
            d["name"]
            for d in sd.query_devices()
            if d.get("max_input_channels", 0) > 0
        ]

    @classmethod
    def set_input_device(cls, idx):
        cls.selected_input_device_index = idx

    @classmethod
    def get_input_device(cls):
        return cls.selected_input_device_index

    @classmethod
    def list_output_devices(cls):
        return [
            d["name"]
            for d in sd.query_devices()
            if d.get("max_output_channels", 0) > 0
        ]

    @classmethod
    def set_output_device(cls, idx):
        cls.selected_output_device_index = idx

    @classmethod
    def get_output_device(cls):
        return cls.selected_output_device_index
