from typing import Optional
import time

import pytesseract
import cv2

from cam import Camera
from stage import Stage, StageDirection, StageStepSize


class System:
    stage: Stage
    hq_cam: Optional[Camera]
    aux_cam: Optional[Camera]

    def __init__(self,
                 stage: Stage,
                 hq_cam: Optional[Camera],
                 aux_cam: Optional[Camera]):
        self.stage = stage
        self.hq_cam = hq_cam
        self.aux_cam = aux_cam

    def homing(self):
        # Test the stage uart connection
        # This errors out if the connection isn't good
        self.stage.idle()

        # Move to the start of the stage
        self.stage.speed(1000)
        self.stage.home(StageDirection.BACKWARD, StageStepSize.QUARTER)
        self.stage.wait()

        # We are at the start of the stage
        # Reset the internal position to 0
        self.stage.set_position(0)

        # TODO(tumbar) Find the fiducial using live cam feed

    def card_id(self) -> str:
        img = self.aux_cam.acquire_array()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # TODO(tumbar) Crop

        # Clean up noise using OTSU thresholding
        # Text is left black, background made white
        ret, img = cv2.threshold(
            img, 146, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
        output = pytesseract.image_to_boxes(
            img, lang='osd', config=tess_config)
        boxes = output.strip().split('\n') if output.strip() else []
        h, w = img.shape

        output = ""
        for b in boxes:
            b = b.split(' ')
            output += b[0]
            img = cv2.rectangle(img,
                                (int(b[1]), h - int(b[2])),
                                (int(b[3]), h - int(b[4])),
                                (0, 255, 0), 2)

        return output

    def single_card(self, path: str = "test"):
        self.stage.speed(1500)

        self.hq_cam.start()

        # TODO(tumbar) Use a better naming scheme
        sensor_names = [str(x) for x in range(12)]
        for sensor in sensor_names:
            # This delay is used to allow the system to stabilize before
            # we acquire an image
            time.sleep(0.2)

            self.hq_cam.acquire(f"{path}-{sensor}.jpg")

            # Each sensor is 350 1/8th steps between each other
            self.stage.relative(350, StageStepSize.EIGHTH)
            self.stage.wait(granularity=0.05)

        self.hq_cam.stop()
