from time import localtime, strftime
import tkinter as tk
from input_commands import input_key
from util import Waiting, Settings
from recording_handler import Recording

settings_filename = "settings.json"


class Window:
    def __init__(self) -> None:
        self.create_util_variables()
        self.handle_input()
        self.create_main_screen()

    def create_util_variables(self):
        self.waiting_for_key = Waiting.No
        self.sleeping = True
        self.recording = False
        self.playing = False
        self.recording_file = Recording()
        self.settings = Settings()
        self.settings.load(settings_filename)

    def create_main_screen(self):
        self.w = tk.Tk(screenName="Input controller")
        self.w.title("Input controller")
        self.w.geometry("800x400+10+10")
        self.w.resizable(False, False)

        self.record_key_label = tk.Label(
            self.w,
            text=self.settings["toggle_record_key"],
            font=('Arial', 15),
            width=10
        )
        self.record_key_label.grid(row=0, column=2, stick='we')

        self.play_key_label = tk.Label(
            self.w,
            text=self.settings["toggle_play_key"],
            font=('Arial', 15),
            width=10
        )
        self.play_key_label.grid(row=0, column=5, stick='we')

        self.log_label = tk.Label(
            self.w,
            text="",
            font=('Arial', 11)
        )
        self.log_label.grid(
            row=1,
            column=3,
            stick='we',
            columnspan=4,
            rowspan=6
        )

        self.loaded_file_label = tk.Label(
            self.w,
            text="No file loaded",
            font=('Arial', 11)
        )
        self.loaded_file_label.grid(
            row=5,
            column=0,
            stick='we',
            columnspan=2,
            rowspan=2
        )

        self.record_key_button = tk.Button(
            self.w,
            text="Toggle recording key",
            font=('Arial', 15),
            command=self.record_start_key
        )
        self.record_key_button.grid(row=0, column=0, columnspan=2)

        self.play_key_button = tk.Button(
            self.w,
            text="Toggle playing key",
            font=('Arial', 15),
            command=self.record_end_key
        )
        self.play_key_button.grid(row=0, column=3, columnspan=2)

        self.sleeping_button = tk.Button(
            self.w,
            text="Sleeping",
            font=('Arial', 15),
            command=self.toggle_sleeping
        )
        self.sleeping_button.grid(row=1, column=0)

        self.save_button = tk.Button(
            self.w,
            text="Save settings",
            font=('Arial', 15),
            command=self.save_settings
        )
        self.save_button.grid(row=1, column=1)

        tk.Label(
            self.w,
            text="Max mousemotion hz",
            font=('Arial', 15)
        ).grid(row=1, column=3)

        self.max_mp_hz_label = tk.Entry(
            self.w,
            font=('Arial', 15),
            width=6
        )
        self.max_mp_hz_label.grid(row=1, column=5)
        self.max_mp_hz_label.insert(0, self.settings["max_mousemotion_hz"])

        tk.Label(
            self.w,
            text="File name",
            font=('Arial', 15)
        ).grid(row=2, column=0)

        self.filename_input = tk.Entry(
            self.w,
            font=('Arial', 15)
        )
        self.filename_input.grid(row=3, column=0, columnspan=2)

        self.savefile_button = tk.Button(
            self.w,
            text="Save file",
            font=('Arial', 15),
            command=self.save_file
        )
        self.savefile_button.grid(row=4, column=0)

        self.save_button = tk.Button(
            self.w,
            text="Load file",
            font=('Arial', 15),
            command=self.load_file
        )
        self.save_button.grid(row=4, column=1)

        self.w.mainloop()

    def record_start_key(self):
        self.record_key_label["text"] = "..."
        self.waiting_for_key = Waiting.Record

    def record_end_key(self):
        self.play_key_label["text"] = "..."
        self.waiting_for_key = Waiting.Play

    def toggle_sleeping(self):
        self.sleeping = not self.sleeping
        self.stop_recording()
        self.sleeping_button["text"] = "Sleeping" if self.sleeping else "Awake"
        self.log(f"Now {self.sleeping_button['text']}")

    def handle_input(self):
        input_key(True, True, self.handle_input_key_press, self.handle_input_key_release, self.handle_mousemotion)

    def handle_input_key_release(self, key):
        if self.recording and str(key) != self.settings["toggle_record_key"]:
            self.recording_file.next_key(key, pressed=False)
            self.update_file_info()

    def handle_mousemotion(self, x, y):
        if self.recording:
            self.recording_file.next_mousemotion((x, y))
            self.update_file_info()

    def handle_input_key_press(self, key):

        if self.waiting_for_key == Waiting.Record:
            self.record_key_label["text"] = key
            self.settings["toggle_record_key"] = key
            self.waiting_for_key = Waiting.No
            self.log(f"Set toggle record key to {key}")

        elif self.waiting_for_key == Waiting.Play:
            self.play_key_label["text"] = key
            self.settings["toggle_play_key"] = key
            self.waiting_for_key = Waiting.No
            self.log(f"Set toggle play key to {key}")

        if str(key) == self.settings["toggle_play_key"]:
            self.try_to_toggle_playing()

        if str(key) == self.settings["toggle_record_key"]:
            self.try_to_toggle_recording()
        elif self.recording:
            self.recording_file.next_key(key, pressed=True)
            self.update_file_info()

    def save_settings(self):
        try:
            self.settings["max_mousemotion_hz"] = str(int(self.max_mp_hz_label.get()))
            self.settings.save(settings_filename)
            self.log("Saved settings")
        except:
            self.log("Error saving max_mousemotion_hz")

    def log(self, message):
        text = str(self.log_label["text"])
        text = text.split("\n")
        if len(text) > 8:
            text.pop()
        text.insert(0, f'[{strftime("%d %b %Y %H:%M:%S", localtime())}] {message}')
        self.log_label["text"] = "\n".join(text)

    def try_to_toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.try_to_start_recording()

    def try_to_start_recording(self):
        if not self.sleeping:
            self.recording = True
            self.recording_file.reset_recording()
            self.recording_file.max_mm_hz = self.settings["max_mousemotion_hz"]
            self.w.title("Input controller: recording")
            self.log("Recording started")

    def stop_recording(self):
        if self.recording:
            self.w.title("Input controller")
            self.log("Recording stopped")
        self.recording = False

    def try_to_toggle_playing(self):
        if (not self.sleeping) and (not self.recording):
            self.recording_file.toggle_playing()
            self.log("Toggled playing")

    def update_file_info(self):
        self.loaded_file_label["text"] = "Recording length: " + str(len(self.recording_file.recording))

    def save_file(self):
        filename = self.filename_input.get()
        try:
            self.recording_file.save(filename)
            self.log(f"Saved file to {filename}")
        except:
            self.log(f"Error saving file {filename}")

    def load_file(self):
        self.recording_file = Recording()
        filename = self.filename_input.get()
        try:
            self.recording_file.load(filename)
            self.update_file_info()
            self.log(f"Loaded file from {filename}")
        except:
            self.log(f"Error loading file {filename}")
