import time

import cv2
import numpy as np

from src.hardware import click


def template_match_and_draw(img, template, threshold=0.8, max_only=True):
    """
    img: 原圖 (BGR)
    template: 模板圖 (BGR)
    """
    draw_img = img.copy()

    # 灰階（一定要）
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tpl_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    h, w = tpl_gray.shape[:2]

    # 模板匹配
    result = cv2.matchTemplate(img_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(max_val, max_loc)
    if not max_only:
        x1, y1 = max_loc
        x2, y2 = x1 + w, y1 + h
        cv2.rectangle(draw_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        return draw_img, [((x1 + x2) // 2, (y1 + y2) // 2), x1, y1]

    # 找匹配位置
    loc = np.where(result >= threshold)
    boxes = []
    for pt in zip(*loc[::-1]):
        x1, y1 = pt
        x2, y2 = x1 + w, y1 + h
        boxes.append(((x1 + x2) // 2, (y1 + y2) // 2, x1, y1))
        cv2.rectangle(draw_img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return draw_img, boxes


def get_role_pos(map_pic):
    hsv = cv2.cvtColor(map_pic, cv2.COLOR_BGR2HSV)
    yellow_lower = np.array([28, 190, 190])
    yellow_upper = np.array([45, 255, 255])
    mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    result = cv2.bitwise_and(map_pic, map_pic, mask=mask)
    kernel = np.ones((5, 5), np.uint8)
    result = cv2.morphologyEx(result, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, result

    # 取最大區塊（通常是角色）
    cnt = max(contours, key=cv2.contourArea)

    x, y, w, h = cv2.boundingRect(cnt)

    cx = x + w // 2
    cy = y + h // 2

    return (cx, cy), result


if __name__ == '__main__':
    from src.win_func.get_win import get_window_from_mouse, capture_window

    window_dict = get_window_from_mouse()
    img = capture_window(window_dict['hwnd'])
    ptn = cv2.imread(r'/data/0001_1.png')
    result_img, boxes = template_match_and_draw(img, ptn, 0.85)
    print("找到數量:", len(boxes))
    print("boxes:", boxes)
    cv2.imwrite("result.png", result_img)
