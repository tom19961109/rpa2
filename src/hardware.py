import time
from pynput.mouse import Button


def click(mouse, x, y):
    mouse.position = (x, y)
    print(x, y)
    time.sleep(0.01)
    mouse.click(Button.left, 1)
