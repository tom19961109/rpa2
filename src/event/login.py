from pynput.keyboard import Key
import win32gui
from cv.img_process import template_match_and_draw
from hardware import click
from utility.params import match_conf, WinTitle
from utility.utility import read_img
import time

from win_func.get_win import get_full_window, find_windows_by_title, move_window


def maple_login(mouse, keyboard, window_list=[]):
    import subprocess
    exe_path = r"D:\0430無題谷主程式\無題谷登入器.exe"
    subprocess.Popen(exe_path)
    time.sleep(30)
    window_dict = {}
    start_find_window_flag = False
    find_window_flag = False
    login_flag = False
    channel_flag = False
    select_role_flag = False
    player_flag = False
    while 1:
        try:
            full_window = get_full_window()
            pth_img = read_img(r'D:\workspace\rpa2\data\login\start.png')
            _, b1 = template_match_and_draw(full_window, pth_img, match_conf)
            if len(b1):
                target = b1[0]
                click(mouse, target[0], target[1])
                time.sleep(30)

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
                pth_img = read_img(r'D:\workspace\rpa2\data\login\login.png')
                _, b2 = template_match_and_draw(full_window, pth_img, match_conf)
                if len(b2):
                    window_dict = move_window(window_dict['hwnd'], 544, 7, window_dict)
                    time.sleep(1)
                    keyboard.press(Key.f9)
                    time.sleep(0.5)
                    keyboard.release(Key.f9)
                    time.sleep(1)

                    full_window = get_full_window()
                    pth_img = read_img(r'D:\workspace\rpa2\data\login\pwd.png')
                    _, b3 = template_match_and_draw(full_window, pth_img, match_conf)
                    if len(b3):
                        target = b3[0]
                        click(mouse, target[0], target[1])
                        pwd = 'memory10505'
                        for c in pwd:
                            keyboard.press(c)
                            time.sleep(0.02)
                            keyboard.release(c)
                        time.sleep(1)

                        pth_img = read_img(r'D:\workspace\rpa2\data\login\login.png')
                        _, b2 = template_match_and_draw(full_window, pth_img, match_conf)
                        target = b2[0]
                        click(mouse, target[0], target[1])
                        logon_flag = True
            if not channel_flag:
                full_window = get_full_window()
                pth_img = read_img(r'D:\workspace\rpa2\data\login\ch3.png')
                _, b1 = template_match_and_draw(full_window, pth_img, match_conf)
                if len(b1):
                    click(mouse, 1011, 355)
                    time.sleep(0.5)
                    keyboard.press(Key.enter)
                    time.sleep(0.3)
                    keyboard.release(Key.enter)
                    channel_flag = True
            if not select_role_flag:
                full_window = get_full_window()
                pth_img = read_img(r'D:\workspace\rpa2\data\login\select_role.png')
                _, b1 = template_match_and_draw(full_window, pth_img, match_conf)
                if len(b1):
                    target = b1[0]
                    click(mouse, target[0], target[1])
                    time.sleep(0.5)

            if not player_flag:
                full_window = get_full_window()
                pth_img = read_img(r'D:\workspace\rpa2\data\login\player.png')
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
        except:
            pass

        time.sleep(1)

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