import json
from time import time, sleep
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key

class Recording:
    def __init__(self):
        self.reset_recording()
        self.max_mm_hz = "1000"
        self.play_c = 0
        self.playing = False

    def load(self, filename):
        with open("recordings/" + filename + ".json", "r") as f:
            self.recording = json.load(f)

    def save(self, filename):
        with open("recordings/" + filename + ".json", "w") as f:
            f.write(json.dumps(self.recording))

    def reset_recording(self):
        self.recording = []
        self.last_timestamp = time()
    
    def next_key(self, key, pressed):
        self.recording.append({
            "delay": (time() - self.last_timestamp),
            "type": "key",
            "mouse": "Button." in str(key),
            "key": str(key),
            "pressed": pressed
        })
        self.last_timestamp = time()
    
    def next_mousemotion(self, coordinates):
        if (time() - self.last_timestamp) >= (1 / int(self.max_mm_hz)):
            self.recording.append({
                "delay": (time() - self.last_timestamp),
                "type": "mousemotion",
                "coordinates": coordinates
            })
            self.last_timestamp = time()
    
    def toggle_playing(self):
        self.playing = not self.playing
        if self.playing:
            self.play_all()

    def play_all(self):
        self.playing = True
        mc = mouse.Controller()
        kc = keyboard.Controller()
        for r in self.recording:
            sleep(float(r["delay"]))
            if not self.playing:
                break
            self.play_next(r, mc, kc)

    def play_next(self, key, mc, kc):
        if key["type"] == "key":
            if key["mouse"]:
                if key["pressed"]:
                    mc.press(eval(key["key"]))
                else:
                    mc.release(eval(key["key"]))
            else:
                if key["pressed"]:
                    kc.press(eval(key["key"]))
                else:
                    kc.release(eval(key["key"]))
        elif key["type"] == "mousemotion":
            mc.position = (key["coordinates"])
