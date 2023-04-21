import logging
from typing import Optional, Tuple

import numpy as np
import pytesseract
import cv2
from pytesseract import TesseractNotFoundError

log = logging.getLogger(__name__)


def compute_error(img: np.ndarray, vx: float, vy: float, cx: float, cy: float):
    """
    Compute the standard deviation of the point errors given
    a line of best fit
    :param img: Image to compute standard deviation on
    :param vx: Delta X of regression.
    :param vy: Delta Y of regression.
    :param cx: Start X point of regression
    :param cy: Start Y point of regression
    :return: Standard deviation in pixels
    """
    v = np.array([vx, vy])
    p = np.array([cx, cy])

    # Find the rotation to align to Y-axis
    # This will make the error between point-to-linear-regression
    # the same as the X-coordinate
    theta = np.arccos(np.dot(v, [0, 1]) / np.linalg.norm(v))

    # Construct a rotation matrix
    r = cv2.getRotationMatrix2D((cx, cy), -180 / np.pi * theta, 1.0)
    rot_img = cv2.warpAffine(img, r, img.shape[0:2], flags=cv2.INTER_LINEAR)

    # Compute the error using only the X coordinate
    # This will be the norm distance of each point to the line
    points = cv2.findNonZero(rot_img).squeeze(1)
    err = (points - p)[:, 0] ** 2

    # Compute the standard deviation
    return np.sqrt(np.einsum('i,i->', err, err) / len(points)), theta


def detect_card_edge(img: np.ndarray,
                     laplacian_threshold: float = 10.0,
                     num_points_threshold: int = 100,
                     standard_deviation_threshold: float = 50.0,
                     vertical_rad_threshold: float = 0.1,
                     debug: bool = False) -> Tuple[Optional[float], np.ndarray]:
    """
    Find the line of best fit for the derivative of an image
    This is essentially like applying a linear regression to
    edges in an image.
    :param img: Image to find best fit for
    :param laplacian_threshold: Threshold of edge to use in regression
    :param num_points_threshold: Drop this image if there is not enough derivative
    :param standard_deviation_threshold: Threshold for linear regression standard deviation
    :param vertical_rad_threshold: Threshold for how vertical the edge of the card should be
    :param debug: Print debug messages
    :return: None if card edge is not in image (a good, relatively vertical line was not found),
             Float from 0.0 - 1.0 indicating where the edge of the card on the image frame
            (0 means left side of the image, 1 means right side)
    """
    # Compress the data to a manageable size
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    scale = 0.4
    img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
    orig_img = img.copy()

    h, w = img.shape

    # Blur the image using a 10x10 averaging kernel
    # Gets rid of gradient noise
    img = cv2.blur(img, (10, 10))

    # Use a laplacian kernel to compute the Gxy gradient
    # across the image to detect edges.
    # We are looking for the edge of the card
    img = cv2.Laplacian(img, cv2.CV_16S, ksize=3)

    # Get image back into 8-bit grayscale
    img = cv2.convertScaleAbs(img)

    # Select the best points
    _, img = cv2.threshold(img, laplacian_threshold, 255, cv2.THRESH_BINARY)

    # Gather a list of potential points on the edge of the sensor card
    points = cv2.findNonZero(img)
    npoints = len(points) if points is not None else 0

    if npoints < num_points_threshold:
        if debug:
            log.info("Found only %d points, no edges", npoints)
        return None, orig_img

    # Perform an L2 norm linear regression to get the line of
    # best fit along the threshold edge
    vx_r, vy_r, cx_r, cy_r = cv2.fitLine(points, cv2.DIST_L2, 0, 0.01, 0.01)
    vx, vy, cx, cy = vx_r[0], vy_r[0], cx_r[0], cy_r[0]

    err, theta = compute_error(img, vx, vy, cx, cy)

    if debug:
        log.info("Edge detection error: %.2f, theta: %.2f, num: %d", err, theta, npoints)

    # This is not an actual edge
    # We just fit some garbage
    if err > standard_deviation_threshold:
        log.info("Not a good line standard deviation: %.2f", err)
        return None, img

    # The line is not vertical enough
    # There are some edges in the image, but they are unlikely
    # to be the card edge since that will be vertical with respect to the
    # HQ Camera
    if abs(theta) > vertical_rad_threshold and abs(theta - np.pi) > vertical_rad_threshold:
        if debug:
            log.info("Line not vertical enough %2.f rad", theta)
        return None, img

    # Solve for center of the parametric line
    # Solve a simple system of equations
    # (vx, vy) * t + (cx, cy) = (1, 0) * s + (0, h / 2)
    center_ts = np.linalg.solve([
        [vx, -1],
        [vy, 0]
    ], [-cx, (h / 2) - cy])

    # Plug in the second parametric parameter into the original parametric equation
    # This will yield the center point along X axis
    # Scale this solution to the width
    pos = center_ts[1] / w
    return pos, img


def card_id(img: np.ndarray,
            scale: float,
            start_row: int,
            start_col: int,
            height: int,
            width: int
            ) -> Tuple[str, np.ndarray]:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Rescale image
    img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))

    # Crop image
    img = img[start_row:start_row + height, start_col:start_col + width]
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Clean up noise using OTSU thresholding
    # Text is left black, background made white
    ret, img = cv2.threshold(
        img, 146, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    tess_config = '--psm 7 --oem 3 outputbase digits'
    try:
        output = pytesseract.image_to_boxes(
            img, lang='osd', config=tess_config)
        boxes = output.strip().split('\n') if output.strip() else []
        output = ""
        for b in boxes:
            b = b.split(' ')
            output += b[0]
    except TesseractNotFoundError:
        output = "0000000"
        log.warning("Make sure tesseract-ocr is installed, continuing without")

    return output, img
