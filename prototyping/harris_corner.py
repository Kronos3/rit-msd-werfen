#!/usr/bin/env python3

from pathlib import Path
import sys

import cv2
import numpy as np


def main():
    img = cv2.imread(sys.argv[1])
    img_path = Path(sys.argv[1])
    # img = cv2.resize(img, (600, 360))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray, 5, 5, 0.10)

    cv2.imshow('Input', img)

    dst = cv2.dilate(dst, None)
    # Threshold for an optimal value, it may vary depending on the image.
    img[dst > 0.1*dst.max()] = [0, 0, 255]

    cv2.imshow('Result', img)
    cv2.imwrite((img_path.parent / (img_path.stem +
                "_processed" + img_path.suffix)).as_posix(), img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
