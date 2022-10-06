from pathlib import Path
import sys

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
    sharpening_kernel = np.array([[0, -1, 0],
                                  [-1, 5, -1],
                                  [0, -1, 0]])
    blur_kernel = np.ones((5, 5)) / 25
    img = cv2.filter2D(img, -1, blur_kernel)
    # img = cv2.filter2D(img, -1, sharpening_kernel)
    # img = cv2.filter2D(img, -1, sharpening_kernel)
    # img = cv2.filter2D(img, -1, kernel)
    # img = cv2.filter2D(img, -1, kernel)
    # return cv2.GaussianBlur(img, (5, 5), 2)
    return img


def threshold(img):
    # return cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 99, 4)
    ret, thresh1 = cv2.threshold(
        img, 146, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    print("Thresholding @%s" % ret)
    return thresh1


def main():
    img = cv2.imread(sys.argv[1], cv2.IMREAD_GRAYSCALE)
    img_path = Path(sys.argv[1])
    # img = cv2.resize(img, (600, 360))

    cv2.imshow('Input', img)

    # img = erode(img)
    # img = blur(img)

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

    img = cv2.putText(img, output, (0, 25), cv2.FONT_HERSHEY_SIMPLEX,
                      1, (0, 0, 0), 2, cv2.LINE_AA)

    cv2.imshow('Result', img)
    cv2.imwrite((img_path.parent / (img_path.stem + "_processed" + img_path.suffix)).as_posix(), img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
