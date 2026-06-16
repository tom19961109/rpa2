import time

import numpy as np
from pynput.keyboard import Key

from src.win_func.get_win import capture_window
from utility.params import jump


def auto_action(action, keyboard):
    if action == "right":
        keyboard.press(Key.right)
        time.sleep(0.12)
        keyboard.release(Key.right)

    elif action == "left":
        keyboard.press(Key.left)
        time.sleep(0.12)
        keyboard.release(Key.left)

    elif action == "up":
        keyboard.press(Key.up)
        time.sleep(0.12)
        keyboard.release(Key.up)

    elif action == "right_jump_fast":
        keyboard.press(Key.right)
        time.sleep(0.05)
        keyboard.press(jump)
        time.sleep(0.07)
        keyboard.release(jump)
        time.sleep(0.05)
        keyboard.press(jump)
        time.sleep(0.07)
        keyboard.release(jump)
        time.sleep(0.05)
        keyboard.release(Key.right)

    elif action == "left_jump_fast":
        keyboard.press(Key.left)
        time.sleep(0.05)
        keyboard.press(jump)
        time.sleep(0.07)
        keyboard.release(jump)
        time.sleep(0.05)
        keyboard.press(jump)
        time.sleep(0.07)
        keyboard.release(jump)
        time.sleep(0.05)
        keyboard.release(Key.left)

    elif action == "right_jump":
        keyboard.press(Key.right)
        time.sleep(0.05)
        keyboard.press(jump)
        time.sleep(0.08)
        keyboard.release(jump)
        time.sleep(0.05)
        keyboard.release(Key.right)

    elif action == "left_jump":
        keyboard.press(Key.left)
        time.sleep(0.05)
        keyboard.press(jump)
        time.sleep(0.08)
        keyboard.release(jump)
        time.sleep(0.05)
        keyboard.release(Key.left)

    elif action == "jump_up":
        keyboard.press(Key.up)
        time.sleep(0.05)
        keyboard.press(jump)
        time.sleep(0.2)
        keyboard.press(jump)
        time.sleep(0.2)
        keyboard.release(jump)
        time.sleep(0.05)
        keyboard.release(Key.up)
        time.sleep(0.3)

    elif action == "jump_down":
        keyboard.press(Key.down)
        time.sleep(0.05)
        keyboard.press(jump)
        time.sleep(0.2)
        keyboard.press(jump)
        time.sleep(0.2)
        keyboard.release(jump)
        time.sleep(0.05)
        keyboard.release(Key.down)

def move_to_target(rx, ry, tx, ty):
    dx = tx - rx
    dy = ty - ry

    if abs(dx) <= 1 and abs(dy) == 0:
        return "arrived"

    # 上下差距大 → 需要跳
    if abs(dx) <= 5 and dy < -7:
        return "jump_up"
    elif abs(dx) <= 1 and dy <= -1:
        return "up"
    elif abs(dx) <= 1 and dy > 1:
        return "jump_down"

    if dx > 20:
        return "right_jump_fast"
    elif dx > 0 and dy < -3:
        return "right_jump"
    elif dx > 0:
        return "right"

    if dx < -20:
        return "left_jump_fast"
    elif dx < -1 and dy < -3:
        return "left_jump"
    elif dx < -1:
        return "left"

    return "left"


def check_black(window_dict, keyboard=None):
    if keyboard is not None:
        print('進傳送點')
        for i in range(2):
            keyboard.press(Key.f11)
            time.sleep(0.1)
        keyboard.release(Key.f11)
        for i in range(10):
            keyboard.press(Key.up)
            time.sleep(0.1)
        keyboard.release(Key.up)

    time.sleep(1.5)
    while True:
        img = capture_window(window_dict['hwnd'])
        if np.mean(img) > 50:
            print("已離開黑畫面")
            break


def find_platform(x, y, platforms, tolerance=3):
    if not platforms:
        return None

    for idx, ((x1, py), (x2, _)) in enumerate(platforms):

        if x1 <= x <= x2 and abs(y - py) <= tolerance:
            return idx

    return None