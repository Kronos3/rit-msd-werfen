import asyncio
import os
import threading
import typing
from typing import Literal, Dict, Tuple, Optional

import cv2
import serial

from fastapi import FastAPI
from fastapi.responses import Response, PlainTextResponse

from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

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


@app.exception_handler(Exception)
def default_exception_handler(request: Request, exc: Exception):
    return PlainTextResponse(str(exc), status_code=500)


class ImageResponse(Response):
    def __init__(self,
                 content: typing.Any = None,
                 scale: float = 0.2,
                 status_code: int = 200,
                 headers: typing.Optional[typing.Mapping[str, str]] = None,
                 media_type: typing.Optional[str] = "image/jpeg",
                 background: typing.Optional[BackgroundTask] = None
                 ):
        self.scale = scale
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content) -> bytes:
        content = cv2.resize(content, (int(content.shape[1] * self.scale), int(content.shape[0] * self.scale)))
        content = cv2.cvtColor(content, cv2.COLOR_BGR2RGB)

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

app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")


@app.get("/")
def index():
    return FileResponse("frontend/dist/index.html")


@app.get("/favicon.ico")
def index():
    return FileResponse("frontend/dist/favicon.ico")


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
    calibrated: bool


@app.get("/stage/status", response_model=StageStatus)
def state_position():
    position = system.stage.get_position()
    return {
        "limit1": system.stage.limit_1,
        "limit2": system.stage.limit_2,
        "estop": system.stage.estop,
        "running": system.stage.running,
        "led": system.stage.led,
        "position": position,
        "calibrated": system.stage.calibrated
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
        encoding: Encodings = "jpeg",
        initial_position: Optional[int] = None,
        scale: float = 0.2,
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
                    initial_position,
                    delay, speed, step, num_captures,
                    StageStepSizesMap[step_size]
            ):
                images.append(image)

            # Now reply to the futures
            for i, image in enumerate(images):
                futures[i].set_result(ImageResponse(image, scale=scale, media_type=f"image/{encoding}"))
        else:
            # Reply to the futures as they come
            # This encodes in-between each step
            for i, image in enumerate(system.single_card_raw(
                    initial_position,
                    delay, speed, step, num_captures,
                    StageStepSizesMap[step_size]
            )):
                futures[i].set_result(ImageResponse(image, scale=scale, media_type=f"image/{encoding}"))

    # Actually execute the request
    # Do this asynchronously
    thread = threading.Thread(target=execute)
    thread.start()

    # Get all the required futures
    return fids


@app.post("/system/align", response_class=ImageResponse)
def system_align(
        light_pwm: float = 0.2,
        coarse_n: int = 400,
        coarse_size: StageStepSizes = "QUATER",
        laplacian_threshold: float = 10.0,
        num_points_threshold: int = 100,
        standard_deviation_threshold: float = 800.0,
        vertical_rad_threshold: float = 0.5,
        step_delay: float = 0.2,
        debug: bool = False
):
    system.stage.led_pwm(light_pwm)

    img, position = system.align(coarse_n, StageStepSizesMap[coarse_size],
                                 laplacian_threshold, num_points_threshold,
                                 standard_deviation_threshold,
                                 vertical_rad_threshold, step_delay,
                                 debug)

    system.stage.led_pwm(0)

    if position is not None:
        center = [int(position * img.shape[1]), img.shape[0] // 2]
        img = cv2.putText(img, str(round(position, 2)), (50, 50),
                          cv2.FONT_HERSHEY_SIMPLEX,
                          1, (0, 255, 0), 2, cv2.LINE_AA)
        img = cv2.circle(img, center, 20, (0, 255, 0), 20)

    return ImageResponse(img, scale=1)


@app.post("/system/card_id", response_class=ImageResponse)
def system_card_id(
        scale: float = 0.4,
        start_row: int = 335,
        start_col: int = 796,
        height: int = 200,
        width: int = 60,
        position: int = 8800,
        light_level: float = 0.010,
):
    system.approach_absolute(position, StageStepSize.EIGHTH)
    system.stage.led_pwm(light_level)

    card_id, img = system.card_id(scale, start_row, start_col, height, width)
    print(card_id)
    return ImageResponse(img, scale=1)


class Mount(BaseModel):
    device: str
    mountpoint: str
    fs_type: str
    options: str
    dump_freq: int
    parallel_fsck: int

    def __init__(self, mtab_line: str):
        device, mountpoint, fs_type, options, dump_freq, parallel_fsck = mtab_line.split()
        super().__init__(
            device=device,
            mountpoint=mountpoint,
            fs_type=fs_type,
            options=options,
            dump_freq=int(dump_freq),
            parallel_fsck=int(parallel_fsck)
        )


@app.post("/linux/mounts")
def linux_usb(
        mount_point_filter: Optional[str] = None,
        fs_type_filter: Optional[str] = None
):
    if mount_point_filter is None and fs_type_filter is None:
        raise ValueError("mount_point and fs_type filters can not both be none")

    # Check for USBs
    out: typing.List[Mount] = []
    with open("/proc/mounts") as mounts:
        for line in mounts:
            filter_is_good = True
            mount = Mount(line)
            if mount_point_filter is not None:
                filter_is_good = filter_is_good and mount_point_filter in mount.mountpoint

            if fs_type_filter is not None:
                filter_is_good = filter_is_good and fs_type_filter in mount.fs_type

            if filter_is_good:
                out.append(mount)

    return out
