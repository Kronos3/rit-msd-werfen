import multiprocessing
import serial

from rit.stage import Stage


def main():
    ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=1.0)
    stage = Stage(ser)

    stage.idle()
    stage.led_pwm(0.2)
    stage.absolute(3000)

    process = multiprocessing.Process(
        name='MyProcess',
        daemon=True
    )
