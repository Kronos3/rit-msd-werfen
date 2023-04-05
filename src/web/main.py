from typing import Literal

import cv2
import serial

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response

from mc.cam import HqCamera, AuxCamera
from mc.stage import StageStepSize, Stage
from mc.system import System

app = FastAPI()

is_dummy = False
if is_dummy:
    system = System(Stage(None), HqCamera(-1), AuxCamera(-1))
else:
    ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=1.0)
    system = System(Stage(ser), HqCamera(1), AuxCamera(0))


class JpegResponse(Response):
    media_type = "image/jpeg"

    def render(self, img) -> bytes:
        return bytearray(cv2.imencode(".jpg", img)[1])


class PngResponse(Response):
    media_type = "image/png"

    def render(self, img) -> bytes:
        return bytearray(cv2.imencode(".png", img)[1])


class TiffResponse(Response):
    media_type = "image/tiff"

    def render(self, img) -> bytes:
        return bytearray(cv2.imencode(".tiff", img)[1])


def cam_acquire_common(cam_name: Literal["hq", "aux"]):
    if cam_name == "hq":
        with system.hq_cam:
            img = system.hq_cam.acquire_array()
    else:
        with system.aux_cam:
            img = system.aux_cam.acquire_array()

    return img


@app.get("/cam/acquire/jpeg/{cam_name}", response_class=JpegResponse)
def cam_acquire(cam_name: Literal["hq", "aux"]):
    return cam_acquire_common(cam_name)


@app.get("/cam/acquire/png/{cam_name}", response_class=PngResponse)
def cam_acquire(cam_name: Literal["hq", "aux"]):
    return cam_acquire_common(cam_name)


@app.get("/cam/acquire/tiff/{cam_name}", response_class=TiffResponse)
def cam_acquire(cam_name: Literal["hq", "aux"]):
    return cam_acquire_common(cam_name)


@app.get("/stage/status")
def stage_status(ping: bool = True):
    # Send an idle packet to update the status flags
    if ping:
        system.stage.idle()

    return {
        "limit1": system.stage.limit_1,
        "limit2": system.stage.limit_2,
        "estop": system.stage.estop,
        "running": system.stage.running,
        "led": system.stage.led,
    }


@app.get("/stage/position")
def state_position():
    position = system.stage.get_position()
    return {
        "limit1": system.stage.limit_1,
        "limit2": system.stage.limit_2,
        "estop": system.stage.estop,
        "running": system.stage.running,
        "led": system.stage.led,
        "position": position
    }


StageStepSizes = Literal[
    "FULL",
    "HALF",
    "QUARTER",
    "EIGHTH"
]

StageStepSizesMap = {
    "FULL": StageStepSize.FULL,
    "HALF": StageStepSize.HALF,
    "QUARTER": StageStepSize.QUARTER,
    "EIGHTH": StageStepSize.EIGHTH
}


@app.get("/system/single_card")
def single_card(
        delay: float = 0.2,
        speed: int = 1500,
        step: int = 350,
        step_size: StageStepSizes = "EIGHTH"):
    sys_step_size = StageStepSizesMap[step_size]

    def streamer():
        for image in system.single_card_raw(delay, speed, step, sys_step_size):
            # processed_image = process_encoding(image, encoding)
            yield bytearray(image)

    return StreamingResponse(streamer())
