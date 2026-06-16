import time
import sys
from pynput.keyboard import Key
from pynput.mouse import Button

from utility.params import ScriptParams


def click(mouse, x, y):
    mouse.position = (x, y)
    print(x, y)
    time.sleep(0.01)
    mouse.click(Button.left, 1)

def on_press(key):
    print(key)
    try:
        if key == Key.f7:
            ScriptParams.status = 'wait'
            return True
        elif key == Key.f8:
            ScriptParams.status = 'running'
            return False
        return None
    except AttributeError:
        pass