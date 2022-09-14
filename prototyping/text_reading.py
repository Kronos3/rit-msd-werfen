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

def laplacian(img):
    dst = cv2.Laplacian(img, cv2.CV_16S, ksize=3)
    # [laplacian]
    # [convert]
    # converting back to uint8
    return cv2.convertScaleAbs(dst)

img = cv2.imread('werfen_text.png', cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (600, 360))

img = erode(img)
# img = laplacian(img)
print(pytesseract.image_to_boxes(img))
cv2.imshow('Result', img)
cv2.waitKey(0)
