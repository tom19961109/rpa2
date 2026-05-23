import ctypes

import cv2
import numpy as np
import win32con
import win32gui
import win32api
import win32ui
import time


def get_root(hwnd):
    while True:
        parent = win32gui.GetParent(hwnd)
        if not parent:
            return hwnd
        hwnd = parent


def get_window_from_mouse():
    print("請點選目標視窗...")
    time.sleep(0.5)
    last_state = False
    while True:
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
            return {'hwnd': hwnd, "rect": rect, 'title': win32gui.GetWindowText(hwnd)}

        last_state = state
        time.sleep(0.01)


def capture_window(hwnd):
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
