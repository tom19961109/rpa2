import os.path
import time

import cv2
import numpy as np
import yaml
import sys
from src.auto import move_to_target, auto_action, check_black, find_platform
from src.cv.img_process import template_match_and_draw, get_role_pos
from src.hardware import click, on_press
from src.win_func.get_win import get_window_from_mouse, capture_window, get_mouse_pos_in_window, monitor_click, \
    get_relative_mouse_pos, move_window
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key
import pynput.keyboard as keyboard_listener
from utility.params import map_h, map_w, ScriptParams, ConfigMode, ConfigScriptPath, ConfigTimes
from utility.utility import read_img


def case1(window_dict, img_path, delta):
    img = capture_window(window_dict['hwnd'])
    ptn = read_img(rf'{img_path}')
    result_img, boxes = template_match_and_draw(img, ptn, 0.85)
    if len(boxes):
        target = boxes[0]
        # delta = (-439, -8)
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

def case2(window_dict, img_path):
    img = capture_window(window_dict['hwnd'])
    ptn = read_img(rf'{img_path}')
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


def auto_run(window_dict, keyboard, ptn_path, pos_list, platform_list=None, retry_times=0):
    if retry_times >= 5:
        return 'replay'

    img = capture_window(window_dict['hwnd'])
    ptn = read_img(ptn_path)
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
            if ScriptParams.status == 'wait':
                return None

            tx, ty = pos
            # target_platform = find_platform(tx, ty, platform_list)
            _, checks = template_match_and_draw(img, ptn, 0.85)
            if not len(checks):
                return None
            arrive_count = 0
            current_pos_count = 0
            pre_sx = 0
            pre_sy = 0
            start = time.time()
            while time.time() - start < 60:
                if ScriptParams.status == 'wait':
                    return None

                img = capture_window(window_dict['hwnd'])
                map_pic = img[y1:y1 + map_h, x1:x1 + map_w]

                pos, _ = get_role_pos(map_pic)
                if pos is None:
                    continue

                sx, sy = get_relative_mouse_pos(window_dict['hwnd'], x1 + pos[0], y1 + pos[1])
                # now_platform = find_platform(sx, sy, platform_list)
                # if target_platform is not None:
                if pre_sx == sx and pre_sy == sy:
                    current_pos_count += 1

                if current_pos_count >= 10:
                    auto_action('up', keyboard)

                pre_sx = sx
                pre_sy = sy
                action = move_to_target(sx, sy, tx, ty)
                if action == "arrived":
                    arrive_count += 1
                    time.sleep(0.2)
                    if arrive_count >= 3:
                        break
                else:
                    arrive_count = 0

                auto_action(action, keyboard)
                print(f"target:{tx, ty}, now: {sx, sy}, action: {action}")

        check_black(window_dict, keyboard)
        img = capture_window(window_dict['hwnd'])
        ptn = read_img(ptn_path)
        result_img, boxes = template_match_and_draw(img, ptn, 0.85)
        if not len(boxes):
            return None
        if tx - sx > 0:
            auto_action('right', keyboard)
        else:
            auto_action('left', keyboard)
        re_run = auto_run(window_dict, keyboard, ptn_path, [pos_list[-1]], retry_times=retry_times + 1)
        if not re_run or re_run == 'replay':
            return re_run
        return 'done'
    return None


def test(window_dict):
    x1 = 0
    y1 = 0
    while 1:
        img = capture_window(window_dict['hwnd'])
        pos, pr_img = get_role_pos(img[0:200, 0:200])
        if pos is None:
            print('Not found pos')
            continue
        sx, sy = get_relative_mouse_pos(window_dict['hwnd'], x1 + pos[0], y1 + pos[1])
        cv2.imwrite("pr_img.png", pr_img)
        print(sx, sy)
    # result_img, boxes = template_match_and_draw(img, ptn, 0.85)
    # if len(boxes):
    #     h, w = ptn.shape[:2]
    #     mx, my, x1, y1 = boxes[0]
    #     pos_list = [(686, 196), (686, 174), (625, 163)]
    #
    #     while True:
    #         img = capture_window(window_dict['hwnd'])
    #         map_pic = img[y1:y1 + map_h, x1:x1 + map_w]
    #
    #         pos, _ = get_role_pos(map_pic)
    #         if pos is None:
    #             continue
    #
    #         sx, sy = get_relative_mouse_pos(window_dict['hwnd'], x1 + pos[0], y1 + pos[1])
    #         # action = move_to_target(sx, sy, tx, ty)
    #         # auto_action(action, keyboard)
    #         print(sx, sy)
    #
    #         now_plat_form = find_platform(sx, sy, platform_list)
    #         print(now_plat_form)
    #         # print(action)


if __name__ == '__main__':
    mouse = MouseController()
    keyboard = KeyboardController()
    listener = keyboard_listener.Listener(on_press=on_press)
    listener.start()

    window_dict = get_window_from_mouse()
    move_window(window_dict['hwnd'], 544, 7)
    print(f'成功將視窗移動到目標位置')
    if ConfigMode == 1:
        test(window_dict)
    else:
        print(2)
        file_name = ConfigScriptPath

        if not os.path.isfile(file_name):
            print(f'找不到檔案: {os.path.abspath(file_name)}')
            input('輸入任意見結束程式')
            sys.exit(0)

        with open(r".\scripts\帽車.yml", "r", encoding="utf-8") as f:
            script_config = yaml.safe_load(f)

        if not script_config.get('script_step'):
            print(f'該檔案目前沒有參數 script_step, 啟動失敗')
            input('輸入任意見結束程式')
            sys.exit(0)

        print(f'成功載入帽車腳本: {os.path.abspath(file_name)}')
        count = 0
        start_time = time.time()
        while count < ConfigTimes:
            for step, step_dict in enumerate(script_config['script_step'], start=1):
                mode = step_dict.get('mode')
                img_path = step_dict.get('img_path')
                pos_list = step_dict.get('pos_list')
                delta = step_dict.get('delta')

                if mode == 'run':
                    if not img_path or not window_dict or not pos_list:
                        print(f'步驟{step}: 資料遺失')
                        print(f'步驟內容: {step_dict}')
                    auto_run(window_dict, keyboard, img_path, pos_list)
                elif mode == 'click':
                    if not img_path or not window_dict:
                        print(f'步驟{step}: 資料遺失')
                        print(f'步驟內容: {step_dict}')
                        break
                    case2(window_dict, img_path)
                elif mode == 'shift_click':
                    if not img_path or not window_dict or not delta:
                        print(f'步驟{step}: 資料遺失')
                        print(f'步驟內容: {step_dict}')
                    case1(window_dict, img_path, delta)
            count += 1
    #     case1(window_dict)
    #     case2(window_dict)
    #     change_channel(window_dict, keyboard)
    #     auto_run(window_dict, keyboard,
    #              r'D:\workspace\rpa2\data\0004.png',
    #              [(578, 189), (625, 189), (717, 185)])
    #     auto_run(window_dict, keyboard,
    #              r'D:\workspace\rpa2\data\0005.png',
    #              [(624, 196), (686, 174), (624, 163)])
    #
    #     auto_run(window_dict, keyboard,
    #              r'D:\workspace\rpa2\data\0006.png',
    #              [(629, 172), (709, 179)])
    #
    #     auto_run(
    #         window_dict, keyboard,
    #         r'D:\workspace\rpa2\data\0007.png',
    #         [(642, 198), (642, 153), (663, 153), (678, 153)],
    #         platform_list=[
    #             [(612, 198), (687, 198)],
    #             [(613, 175), (672, 175)],
    #             [(639, 153), (683, 153)]
    #         ]
    #     )
    #     result = auto_run(window_dict, keyboard,
    #                       r'D:\workspace\rpa2\data\0008.png',
    #                       [(633, 200), (633, 156), (652, 156)])
    #     if result == 'done':
    #         count += 1
    #     total_time = time.time() - start_time
    #     count_avg = 0 if count <= 0 else total_time / count
    #     print(f'total_time: {total_time}, '
    #           f'hat: {count},'
    #           f'avg: {count_avg}')

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
