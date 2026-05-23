import time

import cv2
import numpy as np

from src.auto import move_to_target, auto_action, check_black, find_platform
from src.cv.img_process import template_match_and_draw, get_role_pos
from src.hardware import click
from src.win_func.get_win import get_window_from_mouse, capture_window, get_mouse_pos_in_window, monitor_click, \
    get_relative_mouse_pos, move_window
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key

from utility.params import map_h, map_w


def case1(window_dict):
    img = capture_window(window_dict['hwnd'])
    ptn = cv2.imread(r'D:\workspace\rpa2\data\0001_1.png')
    result_img, boxes = template_match_and_draw(img, ptn, 0.85)
    if len(boxes):
        target = boxes[0]
        delta = (-439, -8)
        click_pos = (target[0] + delta[0], target[1] + delta[1])
        click(mouse,
              click_pos[0] + window_dict['rect'][0],
              click_pos[1] + window_dict['rect'][1])
        time.sleep(1)
        return
        # while 1:
        #     result = get_mouse_pos_in_window(window_dict['hwnd'])
        #     print(result)
        #     time.sleep(1)

    # img = capture_window(window_dict['hwnd'])
    # ptn = cv2.imread(r'D:\workspace\rpa2\data\0001_2.png')
    # result_img, boxes = template_match_and_draw(img, ptn, 0.85)
    # # while 1:
    # #     print(boxes)
    # #     result = get_mouse_pos_in_window(window_dict['hwnd'])
    # #     print(result)
    # #     time.sleep(1)
    # if len(boxes):
    #     target = boxes[0]
    #     delta = (-439, -8)
    #     click_pos = (target[0] + delta[0], target[1] + delta[1])
    #     click(mouse,
    #           click_pos[0] + window_dict['rect'][0],
    #           click_pos[1] + window_dict['rect'][1])
    #     time.sleep(1)
    #     return
    #     # while 1:
    #     #     result = get_mouse_pos_in_window(window_dict['hwnd'])
    #     #     print(result)
    #     #     time.sleep(1)

def case2(window_dict):
    img = capture_window(window_dict['hwnd'])
    ptn = cv2.imread(r'D:\workspace\rpa2\data\0002.png')
    result_img, boxes = template_match_and_draw(img, ptn, 0.85)
    if len(boxes):
        target = boxes[0]
        sx, sy = get_relative_mouse_pos(window_dict['hwnd'], target[0], target[1])
        click(mouse, sx, sy)
        check_black(window_dict, None)
        time.sleep(1)


def change_channel(window_dict, keyboard):
    img = capture_window(window_dict['hwnd'])
    ptn = cv2.imread(r'D:\workspace\rpa2\data\0009.png')
    result_img, boxes = template_match_and_draw(img, ptn, 0.85)
    if len(boxes):
        keyboard.press(Key.esc)
        keyboard.release(Key.esc)
        time.sleep(1)
        keyboard.press(Key.esc)
        keyboard.release(Key.esc)
        time.sleep(2)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(2)
        keyboard.press(Key.right)
        keyboard.release(Key.right)
        time.sleep(2)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        check_black(window_dict)


def auto_run(window_dict, keyboard, ptn_path, pos_list, platform_list=None):
    img = capture_window(window_dict['hwnd'])
    ptn = cv2.imread(ptn_path)
    result_img, boxes = template_match_and_draw(img, ptn, 0.85)
    if len(boxes):
        h, w = ptn.shape[:2]
        mx, my, x1, y1 = boxes[0]
        # pos_list = [(661, 189), (718, 185)]
        for i in range(3):
            keyboard.press(Key.f10)
            time.sleep(0.5)
        keyboard.release(Key.f10)
        tx = 0
        sx = 0
        for pos in pos_list:
            tx, ty = pos
            target_platform = find_platform(tx, ty, platform_list)
            arrive_count = 0
            while True:
                img = capture_window(window_dict['hwnd'])
                map_pic = img[y1:y1 + map_h, x1:x1 + map_w]

                pos, _ = get_role_pos(map_pic)
                if pos is None:
                    continue

                sx, sy = get_relative_mouse_pos(window_dict['hwnd'], x1 + pos[0], y1 + pos[1])
                now_platform = find_platform(sx, sy, platform_list)
                # if target_platform is not None:

                action = move_to_target(sx, sy, tx, ty)
                if action == "arrived":
                    arrive_count += 1
                    time.sleep(0.2)
                    if arrive_count >= 3:
                        break
                else:
                    arrive_count = 0

                auto_action(action, keyboard)
                print(sx, sy, tx, ty)
                print(action)

        check_black(window_dict, keyboard)
        img = capture_window(window_dict['hwnd'])
        ptn = cv2.imread(ptn_path)
        result_img, boxes = template_match_and_draw(img, ptn, 0.85)
        if not len(boxes):
            return None
        if tx - sx > 0:
            auto_action('right', keyboard)
        else:
            auto_action('left', keyboard)
        auto_run(window_dict, keyboard, ptn_path, [pos_list[-1]])
        return 'done'
    return None


def test(img, ptn, platform_list=[]):
    result_img, boxes = template_match_and_draw(img, ptn, 0.85)
    if len(boxes):
        h, w = ptn.shape[:2]
        mx, my, x1, y1 = boxes[0]
        pos_list = [(686, 196), (686, 174), (625, 163)]

        while True:
            img = capture_window(window_dict['hwnd'])
            map_pic = img[y1:y1 + map_h, x1:x1 + map_w]

            pos, _ = get_role_pos(map_pic)
            if pos is None:
                continue

            sx, sy = get_relative_mouse_pos(window_dict['hwnd'], x1 + pos[0], y1 + pos[1])
            # action = move_to_target(sx, sy, tx, ty)
            # auto_action(action, keyboard)
            print(sx, sy)

            now_plat_form = find_platform(sx, sy, platform_list)
            print(now_plat_form)
            # print(action)


if __name__ == '__main__':
    mouse = MouseController()
    keyboard = KeyboardController()
    window_dict = get_window_from_mouse()
    move_window(window_dict['hwnd'], 544, 7)
    test_mode = False
    if test_mode:
        # platform_list = [[(663, 174), (706, 174)],
        #                  [(614, 163), (657, 163)],
        #                  [(629, 181), (635, 181)],
        #                  [(614, 196), (706, 196)]]
        platform_list = [[(612, 198), (687, 198)],
                         [(613, 175), (672, 175)],
                         [(639, 153), (683, 153)]]
        img = capture_window(window_dict['hwnd'])
        ptn = cv2.imread(r'D:\workspace\rpa2\data\0004.png')
        test(img, ptn, platform_list)
        auto_action('jump_up', keyboard)

    else:
        count = 0
        start_time = time.time()
        for i in range(100000):
            case1(window_dict)
            case2(window_dict)
            change_channel(window_dict, keyboard)
            auto_run(window_dict, keyboard,
                     r'D:\workspace\rpa2\data\0004.png',
                     [(625, 189), (717, 185)])
            auto_run(window_dict, keyboard,
                     r'D:\workspace\rpa2\data\0005.png',
                     [(686, 174), (625, 163)])

            auto_run(window_dict, keyboard,
                     r'D:\workspace\rpa2\data\0006.png',
                     [(629, 172), (709, 179)])

            auto_run(
                window_dict, keyboard,
                r'D:\workspace\rpa2\data\0007.png',
                [(642, 198), (642, 153), (679, 153)],
                platform_list=[
                    [(612, 198), (687, 198)],
                    [(613, 175), (672, 175)],
                    [(639, 153), (683, 153)]
                ]
            )
            result = auto_run(window_dict, keyboard,
                              r'D:\workspace\rpa2\data\0008.png',
                              [(633, 200), (633, 156), (653, 156)])
            if result == 'done':
                count += 1
            total_time = time.time() - start_time
            avg = None if count == 0 else total_time / count
            print(f'total_time: {total_time}, '
                  f'hat: {count},'
                  f'avg: {avg}')


    # pos_list = [(633, 200), (633, 178), (633, 156), (653, 156)]

    # img = capture_window(window_dict['hwnd'])
    # ptn = cv2.imread(r'D:\workspace\rpa2\data\0005.png')
    # test(img, ptn, platform_list)
    # auto_action('right', keyboard)
    # auto_action('left', keyboard)
    # auto_action('right_jump', keyboard)
    # auto_action('left', keyboard)
    # auto_action('left', keyboard)
    # auto_action('left', keyboard)
    # auto_action('left', keyboard)
    # auto_action('left', keyboard)
    # auto_action('left', keyboard)
