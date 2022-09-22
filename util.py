import json
from copy import deepcopy

default_settings = {
    "toggle_record_key": "-",
    "toggle_play_key": "=",
    "max_mousemotion_hz": "120"
}

class Waiting:
    Record = 0
    Play = 1
    No = 999

class Settings:
    def __init__(self):
        self.settings = {}

    def load(self, filename):
        with open(filename, "r")as file:
            try:
                self.settings = json.load(file)
            except:
                self.set_default()

    def set_default(self):
        self.settings = deepcopy(default_settings)

    def save(self, filename):
        with open(filename, "w")as file:
            file.write(json.dumps(self.settings))

    def __getitem__(self, key):
        if not key in list(self.settings.keys()):
            self.settings[key] = default_settings[key]
        return self.settings[key]
    
    def __setitem__(self, key, value):
        self.settings[key] = str(value)
