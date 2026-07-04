import pynput
from pynput.keyboard import Key
import win32gui
from cv.img_process import template_match_and_draw
from hardware import click, on_click, double_click, move_mouse
from utility.params import match_conf, WinTitle, exe_path, password, account, channel, out_channel_pos, ScriptParams
from utility.utility import read_img
import time

from win_func.get_win import get_full_window, find_windows_by_title, move_window


def maple_login(mouse, keyboard, window_list=[]):
    # import subprocess
    # subprocess.Popen(exe_path)
    # time.sleep(30)
    window_dict = {}
    start_find_window_flag = False
    find_window_flag = False
    login_flag = False
    channel_flag = False
    select_role_flag = False
    player_flag = False
    while ScriptParams.status == 'running':
        try:
            full_window = get_full_window()
            pth_img = read_img(r'.\data\login\start.png')
            _, b1 = template_match_and_draw(full_window, pth_img, match_conf)
            if len(b1):
                target = b1[0]
                click(mouse, target[0], target[1])
                for i in range(30):
                    time.sleep(1)

            if not start_find_window_flag:
                window_dict_list = find_windows_by_title('無題谷')
                for i in window_dict_list:
                    if i['hwnd'] not in window_list:
                        window_dict = i
                        start_find_window_flag = True
                        break

            if not find_window_flag:
                window_dict_list = find_windows_by_title('[防爆模式] 無題谷')
                for i in window_dict_list:
                    if i['hwnd'] not in window_list:
                        window_dict = i
                        find_window_flag = True
                        break

            if not login_flag:
                win32gui.SetForegroundWindow(window_dict['hwnd'])
                pth_img = read_img(r'.\data\login\login.png')
                _, b2 = template_match_and_draw(full_window, pth_img, match_conf)
                if len(b2):
                    window_dict = move_window(window_dict['hwnd'], 544, 7, window_dict)
                    time.sleep(1)
                    keyboard.press(Key.f9)
                    time.sleep(0.5)
                    keyboard.release(Key.f9)
                    time.sleep(1)

                    full_window = get_full_window()
                    pth_img = read_img(r'.\data\login\logon_failed.png')
                    _, b3 = template_match_and_draw(full_window, pth_img, match_conf)
                    pth_img2 = read_img(r'.\data\login\check.png')
                    _, b4 = template_match_and_draw(full_window, pth_img2, match_conf)
                    if len(b3) and len(b4):
                        target = b4[0]
                        click(mouse, target[0], target[1])

                    full_window = get_full_window()
                    pth_img = read_img(r'.\data\login\pwd2.png')
                    _, b3 = template_match_and_draw(full_window, pth_img, match_conf)
                    if len(b3):
                        target = b3[0]
                        pwd_dx, pwd_dy = 120, 0
                        double_click(mouse, target[0] + pwd_dx, target[1] + pwd_dy - 30)

                        keyboard.press(Key.delete)
                        time.sleep(0.5)
                        keyboard.release(Key.delete)

                        keyboard.press(Key.shift)
                        keyboard.release(Key.shift)
                        for c in account:
                            keyboard.press(c)
                            time.sleep(0.02)
                            keyboard.release(c)
                        time.sleep(1)

                        double_click(mouse, target[0] + pwd_dx, target[1] + pwd_dy)
                        for c in password:
                            keyboard.press(c)
                            time.sleep(0.02)
                            keyboard.release(c)
                        time.sleep(1)

                        pth_img = read_img(r'.\data\login\login.png')
                        _, b2 = template_match_and_draw(full_window, pth_img, match_conf)
                        target = b2[0]
                        click(mouse, target[0], target[1])
                        time.sleep(1)
                        move_mouse(mouse, target[0] - 50, target[1] - 50)


            if not channel_flag:
                full_window = get_full_window()
                pth_img = read_img(r'.\data\login\go.png')
                _, b1 = template_match_and_draw(full_window, pth_img, match_conf)
                if len(b1):
                    pos = out_channel_pos.get(channel)
                    if pos:
                        x, y = pos
                        click(mouse, x, y)
                        time.sleep(0.5)
                        keyboard.press(Key.enter)
                        time.sleep(0.3)
                        keyboard.release(Key.enter)
                        channel_flag = True
                    else:
                        print('找不到頻道座標, 請確認 yml')
            if not select_role_flag:
                full_window = get_full_window()
                pth_img = read_img(r'.\data\login\select_role.png')
                _, b1 = template_match_and_draw(full_window, pth_img, match_conf)
                if len(b1):
                    target = b1[0]
                    click(mouse, target[0], target[1])
                    time.sleep(0.5)

            if not player_flag:
                full_window = get_full_window()
                pth_img = read_img(r'.\data\login\player.png')
                _, b1 = template_match_and_draw(full_window, pth_img, match_conf)
                if len(b1):
                    ea(keyboard)
                    player_flag = True

            if player_flag:
                window_dict_list = find_windows_by_title(WinTitle)
                for i in window_dict_list:
                    if i['hwnd'] not in window_list:
                        window_dict = i
                window_dict = move_window(window_dict['hwnd'], 544, 7, window_dict)
                return window_dict
        except Exception as ex:
            print(f"我跳錯了, 但是不用管我, 我會修好自己, 如果我沒修好自己, 叫麥當勞 MMM\n ex: {ex}")
            check_list = [{'check': '', 'click': r'.\data\login\NO1.png'},
                          {'check': '', 'click': r'.\data\login\NO2.png'},
                          {'check': r'.\data\login\mkd.png', 'click': r'.\data\login\mkd_check.png'}]
            for j in check_list:
                full_window = get_full_window()
                check_flag = True if not j['check'] else False
                if j['check']:
                    check_img = read_img(j['check'])
                    _, b1 = template_match_and_draw(full_window, check_img, match_conf)
                    check_flag = True if len(b1) else False

                pth_img = read_img(j['click'])
                _, b2 = template_match_and_draw(full_window, pth_img, match_conf)
                if check_flag and len(b2):
                    target = b2[0]
                    click(mouse, target[0], target[1])
                    time.sleep(1)
                    move_mouse(mouse, target[0] - 200, target[1] - 200)
                    break

                time.sleep(1)

        time.sleep(1)
    return None


def ea(keyboard):
    keyboard.press(Key.enter)
    time.sleep(0.3)
    keyboard.release(Key.enter)

    keyboard.press(Key.shift)
    keyboard.press('2')
    time.sleep(0.3)
    keyboard.release('2')
    keyboard.release(Key.shift)

    keyboard.press(Key.shift)
    keyboard.press('e')
    time.sleep(0.3)
    keyboard.release('e')
    keyboard.release(Key.shift)

    keyboard.press(Key.shift)
    keyboard.press('a')
    time.sleep(0.3)
    keyboard.release('a')
    keyboard.release(Key.shift)

    keyboard.press(Key.enter)
    time.sleep(0.3)
    keyboard.release(Key.enter)
    keyboard.press(Key.enter)
    time.sleep(0.3)
    keyboard.release(Key.enter)


