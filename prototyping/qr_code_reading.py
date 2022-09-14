import cv2

detector = cv2.QRCodeDetector()

img = cv2.imread('test.png', cv2.IMREAD_GRAYSCALE)
data, bbox, _ = detector.detectAndDecode(img)

print("data: %s" % data)
print(bbox)
