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
    return cv2.GaussianBlur(img,(5,5),2)

def threshold(img):
    ret, thresh1 = cv2.threshold(img,146,255,cv2.THRESH_BINARY_INV)
    print("Thresholding @%s" % ret)
    return thresh1

img = cv2.imread('werfen_text.png', cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (600, 360))

# img = erode(img)
img = blur(img)
img = threshold(img)

boxes = pytesseract.image_to_boxes(img, lang='eng', config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789')
boxes = boxes.strip().split('\n')
h, w = img.shape

for b in boxes:
    b = b.split(' ')
    print(b[0], end="")
    img = cv2.rectangle(img,
                        (int(b[1]), h - int(b[2])),
                        (int(b[3]), h - int(b[4])),
                        (0, 255, 0), 2)

print()
cv2.imshow('Result', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
