import cv2
import numpy as np


def read_img(img_path):
    img = cv2.imdecode(
        np.fromfile(img_path, dtype=np.uint8),
        cv2.IMREAD_COLOR
    )
    return img