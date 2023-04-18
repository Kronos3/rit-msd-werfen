import logging
from typing import Optional, List
import time

import cv2

from rit import processing
from rit.cam import Camera
from rit.stage import Stage, StageDirection, StageStepSize

log = logging.getLogger(__name__)

# Calibrated using GIMP :)
IM_WIDTH_PER_EIGHTH_STEP = 0.0010059171597633137


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

    def approach_relative(self,
                          n: int,
                          size: StageStepSize = StageStepSize.EIGHTH,
                          from_negative: bool = True):
        if from_negative:
            self.stage.relative(n - 300, size)
            self.stage.wait(granularity=0.05)
            self.stage.relative(300, size)
            self.stage.wait(granularity=0.05)
        else:
            self.stage.relative(n + 300, size)
            self.stage.wait(granularity=0.05)
            self.stage.relative(-300, size)
            self.stage.wait(granularity=0.05)

    def approach_absolute(self,
                          pos: int,
                          size: StageStepSize = StageStepSize.EIGHTH,
                          from_negative: bool = True):
        if from_negative:
            self.stage.absolute(pos - 300, size)
            self.stage.wait(granularity=0.05)
        else:
            self.stage.absolute(pos + 300, size)
            self.stage.wait(granularity=0.05)

        self.stage.absolute(pos, size)
        self.stage.wait(granularity=0.05)

    def align(self,
              coarse_n: int = 400,
              coarse_size: StageStepSize = StageStepSize.QUARTER,
              laplacian_threshold: float = 10.0,
              num_points_threshold: int = 100,
              standard_deviation_threshold: float = 50.0,
              vertical_rad_threshold: float = 0.1,
              step_delay: float = 0.1,
              debug: bool = False):

        self.stage.speed(1500)

        # Move to the start of the stage
        self.stage.home(StageDirection.BACKWARD, StageStepSize.QUARTER)
        self.stage.wait(fault_on_limit=False, granularity=0.05)

        try:
            # Start the camera in live stream mode
            self.hq_cam.start(still=False)

            while True:
                self.stage.relative(coarse_n, coarse_size)
                self.stage.wait(granularity=0.05)

                time.sleep(step_delay)

                img = self.hq_cam.acquire_array()
                edge_position, img = processing.detect_card_edge(
                    img, laplacian_threshold,
                    num_points_threshold,
                    standard_deviation_threshold,
                    vertical_rad_threshold, debug
                )

                if debug:
                    yield img

                if edge_position is not None:
                    # Found the edge of the card
                    # Perform the fine motion
                    fine_step = (0.5 - edge_position) / IM_WIDTH_PER_EIGHTH_STEP
                    log.info("Edge position @%.2f", edge_position)
                    log.info("Performing %d steps for fine motion", int(fine_step))

                    print(fine_step)
                    self.approach_relative(int(fine_step), StageStepSize.EIGHTH)

                    time.sleep(step_delay)

                    # Get the final stage position
                    img = self.hq_cam.acquire_array()
                    new_edge_position = processing.detect_card_edge(
                        img, laplacian_threshold,
                        num_points_threshold,
                        standard_deviation_threshold,
                        vertical_rad_threshold, debug
                    )

                    log.info("Card position is now %.2f", new_edge_position if new_edge_position is not None else -1)

                    # Sets the initial calibration value
                    # Sets the stage calibration flag
                    self.stage.set_position(0)

                    return img
        finally:
            # Stop the camera, even on error
            self.hq_cam.stop()

    def single_card(self,
                    initial_position: int,
                    delay: float = 0.2,
                    speed: int = 1500,
                    stage_offsets: List[int] = (),
                    step_size: StageStepSize = StageStepSize.EIGHTH):
        self.stage.speed(speed)
        self.approach_absolute(initial_position, step_size)

        with self.hq_cam:
            for i, offset in enumerate(stage_offsets):
                # This delay is used to allow the system to
                # stabilize before we acquire an image
                if delay > 0:
                    time.sleep(delay)

                yield self.hq_cam.acquire_array()
                log.info("Captured %s / %s images", i + 1, len(stage_offsets))

                # Move to the next sensor and wait for the motion to finish
                self.stage.relative(offset, step_size)
                self.stage.wait(granularity=0.05)
