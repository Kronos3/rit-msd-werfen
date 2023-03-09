from typing import Optional
import time

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

    def single_card(self):
        self.stage.speed(1500)

        self.hq_cam.start()

        # TODO(tumbar) Use a better naming scheme
        sensor_names = [str(x) for x in range(12)]
        for sensor in sensor_names:
            # This delay is used to allow the system to stabilize before
            # we acquire an image
            time.sleep(0.2)

            self.hq_cam.acquire(f"test-{sensor}.jpg")

            # Each sensor is 350 1/8th steps between each other
            self.stage.relative(350, StageStepSize.EIGHTH)
            self.stage.wait()

        self.hq_cam.stop()
