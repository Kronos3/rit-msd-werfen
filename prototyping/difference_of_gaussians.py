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

    low_sigma = cv2.GaussianBlur(gray,(3,3),0.1)
    high_sigma = cv2.GaussianBlur(gray,(5,5),0.4)
    difference_of_gaussians = low_sigma - high_sigma

    thresh = 0.2
    difference_of_gaussians[difference_of_gaussians < thresh * difference_of_gaussians.max()] = 0
    difference_of_gaussians[difference_of_gaussians >= thresh * difference_of_gaussians.max()] = 255

    cv2.imshow('Gaussians', difference_of_gaussians)

    # cv2.imshow('Result', img)
    cv2.imwrite((img_path.parent / (img_path.stem +
                "_processed" + img_path.suffix)).as_posix(), difference_of_gaussians)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
