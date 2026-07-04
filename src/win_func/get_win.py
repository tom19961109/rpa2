import ctypes

import cv2
import mss
import numpy as np
import win32con
import win32gui
import win32api
import win32ui
import win32process
import time
# import mss
from utility.params import WinTitle, ScriptParams


# sct = mss.mss()

def get_full_window(monitor_id=1):
    """
    monitor_id:
        1 = 主螢幕
        0 = 所有螢幕
    return:
        BGR image (OpenCV format)
    """
    with mss.mss() as sct:
        monitor = sct.monitors[monitor_id]
        screenshot = sct.grab(monitor)

        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    return img


def get_root(hwnd):
    while True:
        parent = win32gui.GetParent(hwnd)
        if not parent:
            return hwnd
        hwnd = parent


def get_window_from_mouse():
    start = time.time()
    print("請點選目標視窗...")
    time.sleep(0.5)
    last_state = False

    while time.time() - start < 30:
        state = win32api.GetAsyncKeyState(0x01) & 0x8000

        if state and not last_state:
            x, y = win32api.GetCursorPos()

            hwnd = win32gui.WindowFromPoint((x, y))
            hwnd = get_root(hwnd)

            rect = win32gui.GetWindowRect(hwnd)

            print("HWND:", hwnd)
            print("左上:", (rect[0], rect[1]))
            print("右下:", (rect[2], rect[3]))
            print("標題:", win32gui.GetWindowText(hwnd))
            title = win32gui.GetWindowText(hwnd)
            if WinTitle in title:
                return {'hwnd': hwnd, "rect": rect, 'title': win32gui.GetWindowText(hwnd)}

        last_state = state
        time.sleep(0.01)

    return {}

def find_windows_by_title(target_title):
    results = []

    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)

        if target_title in title:      # 或 title == target_title
            rect = win32gui.GetWindowRect(hwnd)
            results.append({
                "hwnd": hwnd,
                "rect": rect,
                "title": title
            })

    win32gui.EnumWindows(callback, None)
    return results

def force_focus(hwnd):
    if not win32gui.IsWindow(hwnd):
        return

    # 1. 還原視窗（避免最小化/背景）
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    # 2. 解除前景鎖
    fg = win32gui.GetForegroundWindow()

    current = win32api.GetCurrentThreadId()
    fg_tid = win32process.GetWindowThreadProcessId(fg)[0]
    target_tid = win32process.GetWindowThreadProcessId(hwnd)[0]

    win32process.AttachThreadInput(current, fg_tid, True)
    win32process.AttachThreadInput(current, target_tid, True)

    # 3. 強制前景
    win32gui.BringWindowToTop(hwnd)
    win32gui.SetForegroundWindow(hwnd)
    win32gui.SetActiveWindow(hwnd)
    win32gui.SetFocus(hwnd)

    # 4. detach
    win32process.AttachThreadInput(current, fg_tid, False)
    win32process.AttachThreadInput(current, target_tid, False)


def move_window(hwnd, x=505, y=5, window_dict={}):
    rect = win32gui.GetWindowRect(hwnd)
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

    win32gui.SetWindowPos(
        hwnd,
        None,
        x,
        y,
        width,
        height,
        0
    )

    rect = win32gui.GetWindowRect(hwnd)
    window_dict['rect'] = rect
    return window_dict

def capture_window(window_dict, mode=1):
    if mode == 0:
        pass
        # hwnd = window_dict["hwnd"]
        #
        # # Client 左上角的螢幕座標
        # left, top = win32gui.ClientToScreen(hwnd, (0, 0))
        #
        # # Client 大小
        # rect = win32gui.GetClientRect(hwnd)
        # width = rect[2]
        # height = rect[3]
        #
        # monitor = {
        #     "left": left,
        #     "top": top,
        #     "width": width,
        #     "height": height,
        # }
        #
        # img = np.array(sct.grab(monitor))
        # return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    else:
        hwnd = window_dict['hwnd']
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(bitmap)

        # 🔥 正確：用 ctypes 呼叫 PrintWindow
        result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 1)

        bmpinfo = bitmap.GetInfo()
        bmpstr = bitmap.GetBitmapBits(True)

        img = np.frombuffer(bmpstr, dtype='uint8')
        img.shape = (height, width, 4)

        # cleanup
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

        if result != 1:
            print("⚠️ PrintWindow 可能失敗（可能是遊戲/DirectX）")

        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)


def get_mouse_pos_in_window(hwnd):
    # 1. 取得滑鼠螢幕座標
    x, y = win32api.GetCursorPos()

    # 2. 轉成該視窗內座標
    pt = win32gui.ScreenToClient(hwnd, (x, y))

    return {
        "screen": (x, y),
        "client": pt
    }


def get_relative_mouse_pos(hwnd, x, y):
    pt = win32gui.ClientToScreen(hwnd, (x, y))
    return pt


def monitor_click(hwnd, target):
    x1, y1, x2, y2 = target
    tx = (x1 + x2) // 2
    ty = (y1 + y2) // 2

    print("開始監控滑鼠點擊...")

    last_state = False

    while True:
        state = win32api.GetAsyncKeyState(0x01) & 0x8000

        # 只在「按下瞬間」觸發
        if state and not last_state:
            # 1. 取得滑鼠螢幕座標
            sx, sy = win32api.GetCursorPos()

            # 2. 轉 hwnd client 座標
            cx, cy = win32gui.ScreenToClient(hwnd, (sx, sy))

            # 3. 計算相對 target
            dx = cx - tx
            dy = cy - ty

            print("====== CLICK ======")
            print("screen:", (sx, sy))
            print("client:", (cx, cy))
            print("target:", (tx, ty))
            print("delta :", (dx, dy))
            return dx, dy

        last_state = state
        time.sleep(0.01)


if __name__ == '__main__':
    get_window_from_mouse()
