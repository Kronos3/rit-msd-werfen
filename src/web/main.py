from typing import Literal

import cv2
import serial

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response

from mc.cam import HqCamera, AuxCamera, Camera
from mc.stage import StageStepSize, Stage
from mc.system import System

from pydantic import BaseModel

app = FastAPI()

is_dummy = False
if is_dummy:
    system = System(Stage(None), HqCamera(-1), AuxCamera(-1))
else:
    ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=1.0)
    system = System(Stage(None), HqCamera(1), AuxCamera(0))

Encodings = Literal["jpeg", "png", "tiff", "raw"]
Cameras = Literal["hq", "aux"]


class ImageResponse(Response):
    def render(self, content) -> bytes:
        if self.media_type == "image/jpeg":
            img = cv2.imencode(".jpg", content)[1]
        elif self.media_type == "image/png":
            img = cv2.imencode(".png", content)[1]
        elif self.media_type == "image/tiff":
            img = cv2.imencode(".tiff", content)[1]
        else:
            img = content

        return bytes(img)


def get_camera(cam_name: Cameras) -> Camera:
    if cam_name == "hq":
        return system.hq_cam
    else:
        return system.aux_cam


@app.get("/cam/acquire/{cam_name}", response_class=ImageResponse)
def cam_acquire(cam_name: Cameras, encoding: Encodings = "jpeg", start_stop: bool = True):
    camera = get_camera(cam_name)

    if start_stop:
        camera.start()

    img = camera.acquire_array()

    if start_stop:
        camera.stop()

    # Encode the image if requested
    return ImageResponse(img, media_type=f"image/{encoding}")


@app.get("/cam/start/{cam_name}")
def cam_start(cam_name: Cameras):
    get_camera(cam_name).start()


@app.get("/cam/stop/{cam_name}")
def cam_start(cam_name: Cameras):
    get_camera(cam_name).stop()


class StageStatus(BaseModel):
    limit1: bool
    limit2: bool
    estop: bool
    running: bool
    led: bool
    position: int


@app.get("/stage/status", response_model=StageStatus)
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
        num_captures: int = 12,
        step_size: StageStepSizes = "EIGHTH",
        buffer: bool = False
):
    sys_step_size = StageStepSizesMap[step_size]

    if buffer:
        images = []
        for image in system.single_card_raw(
                delay, speed, step, num_captures, sys_step_size
        ):
            images.append(ImageResponse(image, media_type=f"image/{encoding}").body)

        return StreamingResponse(iter(images), media_type="application/octet-stream")
    else:
        return StreamingResponse(
            (ImageResponse(image, media_type=f"image/{encoding}").body
             for image in system.single_card_raw(
                delay, speed, step,
                num_captures, sys_step_size)),
            media_type="application/octet-stream")
