import threading

import cv2
import numpy as np


def read_img(img_path):
    img = cv2.imdecode(
        np.fromfile(img_path, dtype=np.uint8),
        cv2.IMREAD_COLOR
    )
    return img


def input_with_timeout(prompt, timeout=10):
    result = [None]

    def get_input():
        result[0] = input(prompt)

    t = threading.Thread(target=get_input)
    t.daemon = True
    t.start()
    t.join(timeout)

    return result[0]