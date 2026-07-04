import os.path
import time

import cv2
import mss
import numpy as np
import pynput
import yaml
import sys

from event.login import maple_login, ea
from src.auto import move_to_target, auto_action, check_black, find_platform, move_to_target_with_role, auto_action_role
from src.cv.img_process import template_match_and_draw, get_role_pos
from src.hardware import click, on_press
from src.win_func.get_win import get_window_from_mouse, capture_window, get_mouse_pos_in_window, monitor_click, \
    get_relative_mouse_pos, move_window, force_focus, find_windows_by_title, get_full_window
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController, Key
import pynput.keyboard as keyboard_listener
from utility.params import map_h, map_w, ScriptParams, ConfigMode, ConfigScriptPath, ConfigTimes, home_send, \
    attack_multi, WinTitle, match_conf, limit_time, move_delay, attack_duration
from utility.utility import read_img, input_with_timeout
import win32gui


def case1(window_dict, img_path, delta, check_path_list=None, mouse=None):
    img = capture_window(window_dict)
    ptn = read_img(rf'{img_path}')

    if check_path_list:
        flag_list = []
        pass_flag = False
        for i in check_path_list:
            check_img = read_img(rf"{i['img']}")
            flag = i['flag']
            _, c_boxes = template_match_and_draw(img, check_img, match_conf)
            flag_list.append(flag)
            if flag == 'or' and not c_boxes:
                continue
            elif flag == 'or' and c_boxes:
                pass_flag = True
                break
            elif flag == 'not' and c_boxes:
                return
        if 'or' in flag_list and not pass_flag:
            return
    # cv2.imencode('.png', img)[1].tofile('test_img.png')
    # cv2.imencode('.png', ptn)[1].tofile('test_ptn.png')
    result_img, boxes = template_match_and_draw(img, ptn, match_conf)
    if len(boxes):
        target = boxes[0]
        # delta = (-439, -8)
        click_pos = (target[0] + delta[0], target[1] + delta[1])
        click(mouse,
              click_pos[0] + window_dict['rect'][0],
              click_pos[1] + window_dict['rect'][1])
        time.sleep(1)
        if mouse is not None:
            x, y = mouse.position
            mouse.position = (x - 100, y)
        return
        # while 1:
        #     result = get_mouse_pos_in_window(window_dict['hwnd'])
        #     print(result)
        #     time.sleep(1)


def case2(window_dict, img_path, mouse=None):
    img = capture_window(window_dict)
    ptn = read_img(rf'{img_path}')
    result_img, boxes = template_match_and_draw(img, ptn, match_conf)
    if len(boxes):
        target = boxes[0]
        sx, sy = get_relative_mouse_pos(window_dict['hwnd'], target[0], target[1])
        click(mouse, sx, sy)
        check_black(window_dict, None)
        time.sleep(1)
        if mouse is not None:
            x, y = mouse.position
            mouse.position = (x - 100, y)


def case3(window_dict, mouse, img_path, action_list):
    img = capture_window(window_dict)
    ptn = read_img(rf'{img_path}')
    result_img, boxes = template_match_and_draw(img, ptn, match_conf)

    if len(boxes):
        mouse.position = (window_dict['rect'][0] + 50, window_dict['rect'][1] + 50)
        for i in range(3):
            keyboard.press(home_send)
            time.sleep(0.1)
            keyboard.release(home_send)
            time.sleep(0.1)

        img = capture_window(window_dict)
        for i in action_list:
            check_img = read_img(rf"{i['img']}")
            _, c_boxes = template_match_and_draw(img, check_img, match_conf)
            if c_boxes:
                case2(window_dict, i['img'], mouse)


def key_press(window_dict, img_path):
    img = capture_window(window_dict)
    ptn = read_img(rf'{img_path}')
    result_img, boxes = template_match_and_draw(img, ptn, match_conf)
    if len(boxes):
        for i in range(3):
            keyboard.press(home_send)
            time.sleep(0.2)
        keyboard.release(home_send)
        time.sleep(1)


def change_channel(window_dict, keyboard):
    img = capture_window(window_dict)
    ptn = cv2.imread(r'/data/car/0009.png')
    result_img, boxes = template_match_and_draw(img, ptn, match_conf)
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

    img = capture_window(window_dict)
    ptn = read_img(ptn_path)
    result_img, boxes = template_match_and_draw(img, ptn, match_conf)
    if ScriptParams.status == 'wait':
        return None

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
            _, checks = template_match_and_draw(img, ptn, match_conf)
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

                img = capture_window(window_dict)
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
        if ScriptParams.status == 'wait':
            return None

        img = capture_window(window_dict)
        ptn = read_img(ptn_path)
        result_img, boxes = template_match_and_draw(img, ptn, match_conf)
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


def auto_run_with_role(window_dict, keyboard, mouse,
                       ptn_path, role, pos_list, check_path_list):
    img = capture_window(window_dict)
    ptn = read_img(ptn_path)
    result_img, boxes = template_match_and_draw(img, ptn, match_conf)
    if ScriptParams.status == 'wait':
        return None
    start = time.time()
    if len(boxes):
        for pos in pos_list:
            tx, ty = pos
            while time.time() - start < limit_time:
                result_img, boxes = template_match_and_draw(img, ptn, match_conf)
                if not len(boxes):
                    return None

                if ScriptParams.status == 'wait':
                    return None

                img = capture_window(window_dict)
                role_ptn = read_img(role)
                _, role_boxes = template_match_and_draw(img, role_ptn, match_conf)
                if len(role_boxes):
                    rx1, ry1, rx2, ry2 = role_boxes[0]
                    action = move_to_target_with_role(rx1, ry1, tx, ty)
                    print(action)
                    if action == 'arrived':
                        if check_path_list:
                            for i in check_path_list:
                                check_img = read_img(rf"{i['img']}")
                                flag = i['flag']
                                _, c_boxes = template_match_and_draw(img, check_img, match_conf)
                                if flag == 'not' and c_boxes:
                                    return None

                        if ScriptParams.status == 'wait':
                            return None

                        for i in range(2):
                            keyboard.press(attack_multi)
                            time.sleep(0.3)
                        keyboard.release(attack_multi)

                        if ScriptParams.status == 'wait':
                            return None

                        while time.time() - start < attack_duration:
                            keyboard.press(attack_multi)
                            time.sleep(0.3)
                            if ScriptParams.status == 'wait':
                                keyboard.release(attack_multi)
                                return None
                        keyboard.release(attack_multi)
                        print('attack complete')
                        for i in range(2):
                            keyboard.press(Key.up)
                            time.sleep(0.3)
                            print('up press')
                        keyboard.release(Key.up)
                        print('up release')

                        if ScriptParams.status == 'wait':
                            return None
                    else:
                        auto_action_role(action, keyboard)
                        time.sleep(move_delay)
                else:
                    x, y = mouse.position
                    mouse.position = (x - 100, y)

    return None


def test(window_dict):
    x1 = 0
    y1 = 0
    while 1:
        img = capture_window(window_dict)
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
    # window_dict = {'hwnd': 1234}
    mode = input_with_timeout(
        '請選擇模式 \n'
        '0: 自動開啟遊戲並登入 \n'
        '1: 手動選擇視窗 \n'
        '2: 我按錯了, 我要關掉程式 \n'
        '10 秒後將自動設定為手動選擇視窗\n'
    )
    if mode is None:
        mode = '1'

    window_dict_list = find_windows_by_title(WinTitle)
    window_dict = {'hwnd': None}
    mode_time = time.time()
    max_win = 2
    if mode == '1':
        window_dict = get_window_from_mouse()
        if not window_dict:
            print("5 秒後自動關閉程式...")
            time.sleep(5)
            sys.exit(0)
        window_list = [i['hwnd'] for i in window_dict_list if i['hwnd'] != window_dict['hwnd']]
    elif mode == '0' and len(window_dict_list) < max_win:
        ScriptParams.status = 'running'
        print('準備自動開啟遊戲, 你先別急')
        window_list = [i['hwnd'] for i in window_dict_list if i['hwnd'] != window_dict['hwnd']]
        window_dict = maple_login(mouse, keyboard, window_list)
    elif mode == '0' and len(window_dict_list) >= max_win:
        print('遊戲最多只能開兩個視窗, 不能再幫你多開一個唷, 請按任意鍵脫離程式')
        print("5 秒後自動關閉程式...")
        time.sleep(5)
        sys.exit(0)
    elif mode == '2':
        print('掰掰')
        time.sleep(1)
        sys.exit(0)

    window_dict = move_window(window_dict['hwnd'], 544, 7, window_dict)
    print(f'成功將視窗移動到目標位置')
    force_focus(window_dict['hwnd'])
    print(f'聚焦遊戲視窗')
    error_count = 0
    if ConfigMode == 1:
        test(window_dict)
    else:
        win32gui.SetForegroundWindow(window_dict['hwnd'])
        file_name = ConfigScriptPath

        if not os.path.isfile(file_name):
            print(f'找不到檔案: {os.path.abspath(file_name)}')
            print("5 秒後自動關閉程式...")
            time.sleep(5)
            sys.exit(0)

        with open(file_name, "r", encoding="utf-8") as f:
            script_config = yaml.safe_load(f)

        if not script_config.get('script_step'):
            print(f'該檔案目前沒有參數 script_step, 啟動失敗')
            print("5 秒後自動關閉程式...")
            time.sleep(5)
            sys.exit(0)

        print(f'成功載入腳本: {os.path.abspath(file_name)}')
        count = 0
        start_time = time.time()
        ScriptParams.status = 'running'
        ea(keyboard)
        while count < ConfigTimes:
            try:
                if ScriptParams.status == 'wait':
                    print('停止腳本')
                    break

                print(f"count: {count}, error_count: {error_count}")
                for step, step_dict in enumerate(script_config['script_step'], start=1):
                    mode = step_dict.get('mode')
                    img_path = step_dict.get('img_path')
                    role = step_dict.get('role')
                    check_path_list = step_dict.get('check_path_list')
                    action_list = step_dict.get('action_list')
                    pos_list = step_dict.get('pos_list')
                    delta = step_dict.get('delta')

                    if mode == 'run':
                        if not img_path or not window_dict or not pos_list:
                            print(f'步驟{step}: 資料遺失')
                            print(f'步驟內容: {step_dict}')
                        auto_run(window_dict, keyboard, img_path, pos_list)
                    if mode == 'role_run':
                        if not img_path or not window_dict or not pos_list or not role:
                            print(f'步驟{step}: 資料遺失')
                            print(f'步驟內容: {step_dict}')
                        auto_run_with_role(window_dict, keyboard, mouse, img_path, role, pos_list, check_path_list)
                    elif mode == 'click':
                        if not img_path or not window_dict:
                            print(f'步驟{step}: 資料遺失')
                            print(f'步驟內容: {step_dict}')
                            break
                        case2(window_dict, img_path, mouse)
                    elif mode == 'press':
                        if not img_path or not window_dict:
                            print(f'步驟{step}: 資料遺失')
                            print(f'步驟內容: {step_dict}')
                            break
                        key_press(window_dict, img_path)
                    elif mode == 'shift_click':
                        if not img_path or not window_dict or not delta:
                            print(f'步驟{step}: 資料遺失')
                            print(f'步驟內容: {step_dict}')
                        case1(window_dict, img_path, delta, check_path_list, mouse)
                    elif mode == 'home_send':
                        if not img_path or not window_dict or not action_list:
                            print(f'步驟{step}: 資料遺失')
                            print(f'步驟內容: {step_dict}')
                        case3(window_dict, mouse, img_path, action_list)
                count += 1
            except Exception as e:
                window_dict = maple_login(mouse, keyboard, window_list)
                error_count += 1
