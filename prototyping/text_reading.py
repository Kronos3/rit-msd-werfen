import os
from pathlib import Path

import pytesseract
import cv2
import numpy as np


def morph_shape(val):
    if val == 0:
        return cv2.MORPH_RECT
    elif val == 1:
        return cv2.MORPH_CROSS
    elif val == 2:
        return cv2.MORPH_ELLIPSE


def erode(img):
    return cv2.erode(img, np.ones((5, 5), np.uint8))


def blur(img):
    kernel = np.ones((5, 5), np.float32) / 25
    img = cv2.filter2D(img, -1, kernel)
    img = cv2.filter2D(img, -1, kernel)
    return cv2.GaussianBlur(img, (5, 5), 2)


def threshold(img):
    # return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 99, 4)
    ret, thresh1 = cv2.threshold(img, 146, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    print("Thresholding @%s" % ret)
    return thresh1


def main():
    img = cv2.imread('werfen_text.png', cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (600, 360))

    cv2.imshow('Input', img)

    img = erode(img)
    img = blur(img)

    img = threshold(img)

    tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
    output = pytesseract.image_to_boxes(
        img, lang='osd', config=tess_config)
    boxes = output.strip().split('\n') if output.strip() else []
    h, w = img.shape

    output = ""

    print(boxes)

    for b in boxes:
        b = b.split(' ')
        output += b[0]
        img = cv2.rectangle(img,
                            (int(b[1]), h - int(b[2])),
                            (int(b[3]), h - int(b[4])),
                            (0, 255, 0), 2)

    print(output)
    cv2.imshow('Result', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
