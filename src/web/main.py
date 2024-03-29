import asyncio
import datetime
import logging
import os
import shutil
import tempfile
import threading
import time
import typing
from pathlib import Path
from queue import Queue
from typing import Literal, Dict, Tuple, Optional

import cv2
import numpy as np
import serial

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response, PlainTextResponse

from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from rit import processing
from rit.cam import HqCamera, AuxCamera, Camera
from rit.stage import StageStepSize, Stage
from rit.storage import Card, Storage
from rit.system import System

from pydantic import BaseModel

log = logging.getLogger(__name__)

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

Encodings = Literal["jpeg", "png", "tiff"]
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


class SequencedFutureManager:
    _current_id: int
    _futures: Dict[int, Queue]

    def __init__(self):
        self._futures = {}
        self._current_id = 0

    def create(self) -> int:
        fid = self._current_id
        self._current_id += 1

        self._futures[fid] = Queue()
        return fid

    def put(self, fid: int, response):
        self._futures[fid].put(response)

    def get(self, fid: int):
        return self._futures[fid].get()

    def finish(self, fid: int):
        self._futures[fid].put(None)
        del self._futures[fid]


future_manager = FutureManager()
sequenced_future_manager = SequencedFutureManager()

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
def cam_acquire(cam_name: Cameras, scale: float = 0.2, encoding: Encodings = "jpeg", start_stop: bool = True):
    camera = get_camera(cam_name)

    if start_stop:
        camera.start()

    img = camera.acquire_array()

    if start_stop:
        camera.stop()

    # Encode the image if requested
    return ImageResponse(img, scale=scale, media_type=f"image/{encoding}")


@app.get("/cam/preview/start/{cam_name}")
def preview_start(cam_name: Cameras):
    camera = get_camera(cam_name)
    camera.start_preview()


@app.get("/cam/preview/stop/{cam_name}")
def preview_stop(cam_name: Cameras):
    camera = get_camera(cam_name)
    camera.stop_preview()


@app.get("/cam/start/{cam_name}")
def cam_start(cam_name: Cameras):
    get_camera(cam_name).start()


@app.get("/cam/stop/{cam_name}")
def cam_start(cam_name: Cameras):
    get_camera(cam_name).stop()


class Status(BaseModel):
    limit1: bool
    limit2: bool
    estop: bool
    running: bool
    led: bool
    position: int
    calibrated: bool
    hq_preview: bool
    aux_preview: bool


@app.get("/status", response_model=Status)
def state_position():
    position = system.stage.get_position()
    return {
        "limit1": system.stage.limit_1,
        "limit2": system.stage.limit_2,
        "estop": system.stage.estop,
        "running": system.stage.running,
        "led": system.stage.led,
        "position": position,
        "calibrated": system.stage.calibrated,
        "hq_preview": system.hq_cam.preview,
        "aux_preview": system.aux_cam.preview,
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
    system.stage.wait()


@app.post("/stage/absolute")
def stage_absolute(n: int, size: StageStepSizes = "EIGHTH", ignore_limits: bool = False):
    system.stage.absolute(n, StageStepSizesMap[size], ignore_limits)
    system.stage.wait()


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


@app.get("/sfuture/{fid}")
def get_sequenced_future(fid: int):
    res = sequenced_future_manager.get(fid)
    if res is None:
        raise HTTPException(status_code=204, detail="No more content")
    return res


@app.post("/system/single_card")
async def single_card(
        encoding: Encodings = "jpeg",
        initial_position: int = 2500,
        light_pwm: float = 0.2,
        scale: float = 0.2,
        delay: float = 0.2,
        speed: int = 1500,
        stage_offsets: typing.Annotated[typing.List[int], Query()] = (350, 350, 350, 350, 350, 350),
        step_size: StageStepSizes = "QUARTER",
        buffer: bool = False
):
    # Generate the futures for the frontend to request these images
    futures = []
    fids = []
    for _ in stage_offsets:
        fid, future = future_manager.create()
        futures.append(future)
        fids.append(fid)

    def execute():
        system.stage.led_pwm(light_pwm)
        if buffer:
            # First gather all the images
            images = []
            for image in system.single_card(
                    initial_position,
                    delay, speed, stage_offsets,
                    StageStepSizesMap[step_size]
            ):
                images.append(image)

            # Now reply to the futures
            for i, image in enumerate(images):
                futures[i].set_result(ImageResponse(image, scale=scale, media_type=f"image/{encoding}"))
        else:
            # Reply to the futures as they come
            # This encodes in-between each step
            for i, image in enumerate(system.single_card(
                    initial_position,
                    delay, speed, stage_offsets,
                    StageStepSizesMap[step_size]
            )):
                futures[i].set_result(ImageResponse(image, scale=scale, media_type=f"image/{encoding}"))
        system.stage.led_pwm(0)

    # Actually execute the request
    # Do this asynchronously
    thread = threading.Thread(target=execute)
    thread.start()

    # Get all the required futures
    return fids


@app.post("/system/align")
def system_align(
        light_pwm: float = 0.2,
        coarse_n: int = 300,
        coarse_size: StageStepSizes = "QUARTER",
        laplacian_threshold: float = 12.0,
        num_points_threshold: int = 100,
        standard_deviation_threshold: float = 100.0,
        vertical_rad_threshold: float = 0.5,
        step_delay: float = 0.2
):
    system.stage.led_pwm(light_pwm)
    for _ in system.align(coarse_n, StageStepSizesMap[coarse_size],
                          laplacian_threshold, num_points_threshold,
                          standard_deviation_threshold,
                          vertical_rad_threshold, step_delay,
                          debug=False):
        pass
    system.stage.led_pwm(0)


@app.post("/system/debug_align")
async def system_debug_align(
        light_pwm: float = 0.2,
        coarse_n: int = 300,
        coarse_size: StageStepSizes = "QUARTER",
        laplacian_threshold: float = 12.0,
        num_points_threshold: int = 100,
        standard_deviation_threshold: float = 100.0,
        vertical_rad_threshold: float = 0.5,
        step_delay: float = 0.2
):
    fid = sequenced_future_manager.create()

    def run_alignment():
        system.stage.led_pwm(light_pwm)
        for img in system.align(coarse_n, StageStepSizesMap[coarse_size],
                                laplacian_threshold, num_points_threshold,
                                standard_deviation_threshold,
                                vertical_rad_threshold, step_delay,
                                debug=True):
            sequenced_future_manager.put(fid, ImageResponse(img, scale=1))
        system.stage.led_pwm(0)
        sequenced_future_manager.finish(fid)

    threading.Thread(target=run_alignment, daemon=True).start()
    return fid


@app.post("/system/card_id")
def system_card_id(
        scale: float = 1,
        start_row: int = 1150,
        end_row: int = 1300,
        start_col: int = 600,
        end_col: int = 1250,
        position: int = 8200,
        light_level: float = 0,
        step_size: StageStepSizes = "QUARTER",
        return_img: bool = True
):
    system.approach_absolute(position, size=StageStepSizesMap[step_size])
    system.stage.led_pwm(light_level)

    with system.aux_cam:
        img = system.aux_cam.acquire_array()
        card_id, img = processing.card_id(img, scale, start_row, end_row, start_col, end_col)

    if return_img:
        return ImageResponse(img, scale=1)
    else:
        return card_id


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


@app.post("/linux/unmount")
def linux_unmount(mountpoint: str):
    out = os.system(f"umount {mountpoint}")
    assert out == 0, "Umount call failed"


class SingleCardParameters(BaseModel):
    encoding: Encodings = "jpeg"
    light_pwm: float = 0.2
    initial_position: int = 2500
    scale: float = 0.2
    delay: float = 0.2
    speed: int = 2000
    stage_offsets: typing.List[int] = (350, 350, 350, 350, 350)
    step_size: StageStepSizes = "QUARTER"


class CardIDParameters(BaseModel):
    scale: float = 1,
    start_row: int = 1150,
    end_row: int = 1300,
    start_col: int = 600,
    end_col: int = 1250,
    position: int = 8200,
    light_level: float = 0
    step_size: StageStepSizes = "QUARTER"


class RunParams(BaseModel):
    sensor: Optional[SingleCardParameters]
    card_id: Optional[CardIDParameters]
    path: str


def rename_card_id(path: str, subdir: str, to_id: str):
    mount_point_path = Path(path)
    assert mount_point_path.exists() and mount_point_path.is_dir()

    stor = Storage.open(mount_point_path)
    for card in stor.cards:
        if subdir == card.subdir_path:
            assert (mount_point_path / card.subdir_path).exists() and (mount_point_path / card.subdir_path).is_dir()

            new_subdir_items = card.subdir_path.split("-")
            new_subdir_items[-1] = to_id
            new_subdir = "-".join(new_subdir_items)

            with (mount_point_path / card.subdir_path / "card_id.gt.txt").open("w+") as f:
                f.write(to_id)

            os.rename(
                mount_point_path / card.subdir_path,
                mount_point_path / new_subdir
            )

            card.subdir_path = new_subdir
            card.card_id = to_id
            stor.save()
            return {
                "card_id": to_id,
                "subdir": new_subdir
            }

    raise ValueError("No card acquisition found")


@app.post("/system/run")
async def run(request: RunParams):
    mount_point_path = Path(request.path)
    assert mount_point_path.exists() and mount_point_path.is_dir()

    if request.sensor is None:
        request.sensor = SingleCardParameters()
    if request.card_id is None:
        request.card_id = CardIDParameters()

    # Generate the futures for the frontend to request these images
    futures = []
    fids = []
    for _ in range(len(request.sensor.stage_offsets) + 2):
        fid, future = future_manager.create()
        futures.append(future)
        fids.append(fid)

    encoding_queue = Queue[Tuple[int, np.ndarray]]()

    acquisition_time = datetime.datetime.now()
    subdir = acquisition_time.strftime(f"%Y-%m-%d-%H-%M-%S-tmp")
    output_path = mount_point_path / subdir
    output_path.mkdir(parents=True)

    def encode_worker():
        while True:
            i, img = encoding_queue.get()

            if request.sensor.encoding == "jpeg":
                cv2.imwrite(str(output_path / f"{i}.jpg"), img)
            elif request.sensor.encoding == "png":
                cv2.imwrite(str(output_path / f"{i}.png"), img)
            elif request.sensor.encoding == "tiff":
                cv2.imwrite(str(output_path / f"{i}.tiff"), img)

            encoding_queue.task_done()

    # Boot up the encoder worker
    threading.Thread(target=encode_worker, daemon=True).start()

    def execute():
        # Run all the sensor captures
        # Start up both cameras to reduce startup overhead
        try:
            system.hq_cam.start()

            system.stage.led_pwm(request.sensor.light_pwm)

            system.stage.speed(request.sensor.speed)
            system.approach_absolute(request.sensor.initial_position, size=StageStepSizesMap[request.sensor.step_size])
            for i, pos in enumerate(request.sensor.stage_offsets):
                if request.sensor.delay > 0:
                    time.sleep(request.sensor.delay)

                img = system.hq_cam.acquire_array()

                # Queue the image to be encoded and written to disk
                encoding_queue.put((i, img))

                log.info("Acquired %d/%d", i + 1, len(request.sensor.stage_offsets))

                # No need to buffer since we are encoding with preview size
                futures[i].set_result(ImageResponse(img, scale=request.sensor.scale))

                # Move to the next image
                system.stage.relative(
                    pos,
                    StageStepSizesMap[request.sensor.step_size],
                )
                system.stage.wait(granularity=0.05)

            # Move to where the out camera can take an image
            # (Move quickly)
            log.info("Detecting card ID")
            system.stage.led_pwm(request.card_id.light_level)
            system.approach_absolute(request.card_id.position, size=StageStepSizesMap[request.card_id.step_size])

            # Save images and files to disk
            # Do this while we wait for the card to move to Aux position
            card = Card(
                card_id="tmp",
                stage_offsets=request.sensor.stage_offsets,
                acquisition_time=acquisition_time,
                subdir_path=subdir,
                image_format=request.sensor.encoding
            )

            # Grab an aux image and process it
            with system.aux_cam:
                card_id_img = system.aux_cam.acquire_array()
            card_id, card_id_img_proc = processing.card_id(
                card_id_img,
                request.card_id.scale,
                request.card_id.start_row,
                request.card_id.end_row,
                request.card_id.start_col,
                request.card_id.end_col
            )

            # This encoding should be pretty fast since the image is tiny
            cv2.imwrite(str(output_path / f"card_id.png"), card_id_img_proc)
            with (output_path / f"card_id.gt.txt").open("w+") as f:
                f.write(card_id)

            # Write to the listings file
            Storage.open(mount_point_path).add_card(card)

            # Resolve the final future
            futures[-2].set_result(ImageResponse(card_id_img_proc, scale=1))

            encoding_queue.join()

            futures[-1].set_result(rename_card_id(request.path, subdir, card_id))

        finally:
            system.stage.led_pwm(0)
            system.hq_cam.stop()

    # Actually execute the request
    # Do this asynchronously
    thread = threading.Thread(target=execute)
    thread.start()

    # Get all the required futures
    return fids


@app.post("/system/rename")
def rename(
        path: str,
        subdir: str,
        to_id: str
):
    return rename_card_id(path, subdir, to_id)


@app.get("/system/cards")
def get_cards(path: str):
    p_path = Path(path)
    assert p_path.exists() and p_path.is_dir()

    stor = Storage.open(p_path)
    return stor.cards


@app.get("/system/card/view")
def get_card(path: str, subdir: str, img: int, encoding: Encodings):
    read_path = Path(path) / subdir
    assert read_path.is_dir()

    if encoding == "jpeg":
        img = cv2.imread(str(read_path / f"{img}.jpg"))
    elif encoding == "png":
        img = cv2.imread(str(read_path / f"{img}.png"))
    elif encoding == "tiff":
        img = cv2.imread(str(read_path / f"{img}.tiff"))
    else:
        assert False, f"Invalid Encoding {encoding}"

    return ImageResponse(img)


@app.get("/system/card/delete")
def delete_card(path: str, subdir: str):
    # Search for this card in the listings
    stor = Storage.open(Path(path))
    del_idx = -1
    for i, card in enumerate(stor.cards):
        if card.subdir_path == subdir:
            del_idx = i
            break

    assert del_idx != -1, f"Subdir {subdir} not found in {path}"
    del stor.cards[del_idx]
    stor.save()

    del_path = Path(path) / subdir
    assert del_path.is_dir()
    shutil.rmtree(del_path)


@app.get("/system/card/download")
def card_download(path: str, subdir: str):
    fd, zip_path = tempfile.mkstemp(".zip")

    def cleanup():
        os.remove(zip_path)

    log.info("Zipping %s into %s", subdir, zip_path)
    cleanup()
    out = os.system(f"zip -rj {zip_path} {path}/{subdir}/")
    assert out == 0, "Zip call failed"

    return FileResponse(zip_path, background=BackgroundTask(cleanup))
