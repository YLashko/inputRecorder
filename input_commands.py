from time import sleep
from pynput import mouse
from pynput import keyboard

def input_key(record_keyboard, record_mouse, process_key_press, process_key_release, process_mousemotion):

    def on_press(key):
        process_key_press(key)

    def on_release(key):
        process_key_release(key)

    def on_move(x, y):
        process_mousemotion(x, y)

    def on_click(x, y, button, pressed):
        if pressed:
            process_key_press(button)
        else:
            process_key_release(button)

    def on_scroll(x, y, dx, dy):
        pass

    if record_keyboard:
        listener_keyboard = keyboard.Listener(
            on_press=on_press,
            on_release=on_release,
            suppress=False)
        listener_keyboard.start()

    if record_mouse:
        listener_mouse = mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll,
            suppress=False)
        listener_mouse.start()
