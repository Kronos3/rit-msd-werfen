import asyncio
import os
import threading
from typing import Literal, Dict, Tuple

import cv2
import serial

from fastapi import FastAPI
from fastapi.responses import Response

from fastapi.middleware.cors import CORSMiddleware

from mc.cam import HqCamera, AuxCamera, Camera
from mc.stage import StageStepSize, Stage
from mc.system import System

from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

is_dummy = os.getenv("WERFEN_DUMMY")
serial_file = os.getenv("WERFEN_SERIAL")
if is_dummy:
    system = System(Stage(None), HqCamera(-1), AuxCamera(-1))
else:
    if serial_file:
        ser = serial.Serial(serial_file, 115200, timeout=1.0)
    else:
        ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=1.0)
    system = System(Stage(ser), HqCamera(1), AuxCamera(0))

Encodings = Literal["jpeg", "png", "tiff", "raw"]
Cameras = Literal["hq", "aux"]


class ImageResponse(Response):
    def render(self, content) -> bytes:
        content = cv2.resize(content, (int(content.shape[1] * 0.2), int(content.shape[0] * 0.2)))

        if self.media_type == "image/jpeg":
            img = cv2.imencode(".jpg", content)[1]
        elif self.media_type == "image/png":
            img = cv2.imencode(".png", content)[1]
        elif self.media_type == "image/tiff":
            img = cv2.imencode(".tiff", content)[1]
        else:
            img = content

        return bytes(img)


class FutureManager:
    _current_id: int
    _futures: Dict[int, asyncio.Future]

    def __init__(self):
        self._futures = {}
        self._current_id = 0

    def create(self) -> Tuple[int, asyncio.Future]:
        fid = self._current_id
        self._current_id += 1

        out = asyncio.Future()
        self._futures[fid] = out

        return fid, out

    def get(self, fid: int) -> asyncio.Future:
        return self._futures[fid]

    def delete(self, fid: int):
        del self._futures[fid]


future_manager = FutureManager()


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


@app.post("/stage/relative")
def stage_relative(n: int, size: StageStepSizes, ignore_limits: bool = False):
    system.stage.relative(n, StageStepSizesMap[size], ignore_limits)


@app.post("/stage/absolute")
def stage_absolute(n: int, size: StageStepSizes = "EIGHTH", ignore_limits: bool = False):
    system.stage.absolute(n, StageStepSizesMap[size], ignore_limits)


@app.post("/stage/set_position")
def stage_absolute(position: int):
    system.stage.set_position(position)


@app.post("/stage/speed")
def stage_speed(hz: int):
    system.stage.speed(hz)


@app.post("/stage/led_pwm")
def stage_speed(pwm: float):
    system.stage.led_pwm(pwm)


@app.post("/stage/step_off")
def stage_speed(n: int, size: StageStepSizes = "EIGHTH"):
    system.stage.switch_step_off(StageStepSizesMap[size], n)


@app.get("/system/estop")
def estop(stop: bool):
    if stop:
        system.stage.emergency_stop()
    else:
        system.stage.emergency_clear()


@app.get("/future/{fid}")
async def get_future(fid: int):
    img = await future_manager.get(fid)

    # Free up resources (should free the image)
    future_manager.delete(fid)
    return img


@app.post("/system/single_card")
async def single_card(
        encoding: Encodings = "tiff",
        delay: float = 0.2,
        speed: int = 1500,
        step: int = 350,
        num_captures: int = 12,
        step_size: StageStepSizes = "EIGHTH",
        buffer: bool = False
):
    # Generate the futures for the frontend to request these images
    futures = []
    fids = []
    for _ in range(num_captures):
        fid, future = future_manager.create()
        futures.append(future)
        fids.append(fid)

    def execute():
        if buffer:
            # First gather all the images
            images = []
            for image in system.single_card_raw(
                    delay, speed, step, num_captures,
                    StageStepSizesMap[step_size]
            ):
                images.append(image)

            # Now reply to the futures
            for i, image in enumerate(images):
                futures[i].set_result(ImageResponse(image, media_type=f"image/{encoding}"))
        else:
            # Reply to the futures as they come
            # This encodes in-between each step
            for i, image in enumerate(system.single_card_raw(
                    delay, speed, step, num_captures,
                    StageStepSizesMap[step_size]
            )):
                futures[i].set_result(ImageResponse(image, media_type=f"image/{encoding}"))

    # Actually execute the request
    # Do this asynchronously
    thread = threading.Thread(target=execute)
    thread.start()

    # Get all the required futures
    return fids
