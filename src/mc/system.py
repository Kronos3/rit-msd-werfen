import logging
from typing import Optional
import time

import pytesseract
import cv2

from mc.cam import Camera
from mc.stage import Stage, StageDirection, StageStepSize


log = logging.getLogger(__name__)


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
        self.stage.wait(fault_on_limit=False)

        # We are at the start of the stage
        # Reset the internal position to 0
        self.stage.set_position(0)

        # TODO(tumbar) Find the fiducial using live cam feed

    def card_id(self) -> str:
        with self.aux_cam:
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

    def single_card(self,
                    initial_position: Optional[str] = None,
                    delay_s: str = "0.2", path: str = "test"):
        i = 0
        for image in self.single_card_raw(
                int(initial_position) if initial_position is not None else None,
                float(delay_s)):
            # TODO(tumbar) Create a better naming scheme
            cv2.imwrite(f"{path}-{i}.jpg", image)
            i += 1

    def single_card_raw(self,
                        initial_position: Optional[int] = None,
                        delay: float = 0.2,
                        speed: int = 1500,
                        step: int = 350,
                        num_captures: int = 12,
                        step_size: StageStepSize = StageStepSize.EIGHTH):
        self.stage.speed(speed)

        if initial_position is not None:
            # Move in from the same direction that we are iterating
            # over the cards. This way the motor does not need to change
            # direction causing a single Y-axis shift.
            self.stage.absolute(initial_position - 300)
            self.stage.wait()
            self.stage.absolute(initial_position)
            self.stage.wait()

        with self.hq_cam:
            for i in range(num_captures):
                # This delay is used to allow the system to
                # stabilize before we acquire an image
                if delay > 0:
                    time.sleep(delay)

                yield self.hq_cam.acquire_array()
                log.info("Captured %s / %s images", i + 1, num_captures)

                # Move to the next sensor and wait for the motion to finish
                self.stage.relative(step, step_size)
                self.stage.wait(granularity=0.05)
