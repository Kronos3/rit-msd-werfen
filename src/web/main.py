from typing import Literal
import base64

import cv2
import serial

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

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


Encodings = Literal["jpeg", "png", "tiff", "raw"]


def process_encoding(img, encoding: Encodings):
    if encoding == "jpeg":
        return cv2.imencode(".jpg", img)[1]
    elif encoding == "png":
        return cv2.imencode(".png", img)[1]
    elif encoding == "tiff":
        return cv2.imencode(".tiff", img)[1]
    return img


@app.get("/cam/acquire/{cam_name}")
def cam_acquire(cam_name: Literal["hq", "aux"], encoding: Encodings = "jpeg"):
    if cam_name == "hq":
        with system.hq_cam:
            img = system.hq_cam.acquire_array()
    else:
        with system.aux_cam:
            img = system.aux_cam.acquire_array()

    # Encode the image if requested

    return bytearray(process_encoding(img, encoding))


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
        encoding: Encodings = "tiff",
        delay: float = 0.2,
        speed: int = 1500,
        step: int = 350,
        step_size: StageStepSizes = "EIGHTH"):
    sys_step_size = StageStepSizesMap[step_size]

    def streamer():
        for image in system.single_card_raw(delay, speed, step, sys_step_size):
            processed_image = process_encoding(image, encoding)
            yield bytearray(processed_image)

    return StreamingResponse(streamer())
