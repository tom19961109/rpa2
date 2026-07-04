import time
import sys
from pynput.keyboard import Key
from pynput.mouse import Button

from utility.params import ScriptParams


def move_mouse(mouse, x=0, y=0):
    mouse.position = (x, y)

def click(mouse, x, y):
    mouse.position = (x, y)
    print(x, y)
    time.sleep(0.01)
    mouse.click(Button.left, 1)

def double_click(mouse, x, y):
    mouse.position = (x, y)
    mouse.press(Button.left)
    time.sleep(0.2)
    mouse.release(Button.left)
    mouse.press(Button.left)
    time.sleep(0.2)
    mouse.release(Button.left)

def on_press(key):
    # print(key)
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

def on_click(x, y, button, pressed):
    if pressed:
        print(f"你點了：({x}, {y})")