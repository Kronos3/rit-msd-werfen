import os
import time
import traceback
import readline
from typing import List

import serial

from mc.cam import HqCamera, AuxCamera
from mc.stage import Stage, StageStepSize, StageDirection
from mc.system import System


class Cli:
    SIZE_TO_E = {
        1: StageStepSize.FULL,
        2: StageStepSize.HALF,
        4: StageStepSize.QUARTER,
        8: StageStepSize.EIGHTH,
    }
    IDLE = "i", "idle"
    WAIT = "w", "wait"
    RELATIVE = "r", "relative"
    ABSOLUTE = "a", "absolute"
    SPEED = "s", "speed"
    CANCEL = "c", "cancel", "stop"
    HOME = "h", "home"
    SET_POSITION = "sp", "set_position"
    GET_POSITION = "gp", "get_position"
    LED_PWM = "pwm", "led_pwm",
    LED_VOLTAGE = "v", "led_voltage"
    LED_KP = "kp", "led_pid_kp"
    LED_KI = "ki", "led_pid_ki"
    LED_KD = "kd", "led_pid_kd"
    DEBOUNCE = "d", "debounce"
    HELP = "?", "help"
    QUIT = "q", "quit"
    CLEAR = "clear",
    SLEEP = "sleep",
    RUN = "run",

    def __init__(self, system: System):
        self.system = system

    @staticmethod
    def parse(command: str) -> List[str]:
        """
        Parse a raw command into tokens able to execute()
        :param command: Full command string
        :return:
        """
        comment_idx = command.find(";")
        if comment_idx >= 0:
            command = command[:comment_idx]
        return [i for i in command.lower().strip().split(" ") if i]

    def execute(self, command: List[str]):
        if not command:
            return

        op = command[0]
        if op in self.IDLE:
            self.system.stage.idle()
            print(f"LIMIT 1: {'ON' if self.system.stage.limit_1 else 'OFF'}\n"
                  f"LIMIT 2: {'ON' if self.system.stage.limit_2 else 'OFF'}\n"
                  f"E-STOP: {'ON' if self.system.stage.estop else 'OFF'}\n"
                  f"RUNNING: {'ON' if self.system.stage.running else 'OFF'}\n"
                  f"LED: {'ON' if self.system.stage.led else 'OFF'}")
        elif op in self.WAIT:
            assert len(command) <= 3, command
            timeout = 0.0
            granularity = 0.1
            if len(command) >= 2:
                timeout = float(command[1])
            if len(command) == 3:
                granularity = float(command[2])
            self.system.stage.wait(timeout, granularity)
        elif op in self.RELATIVE:
            assert len(command) == 3, command
            pos = int(command[1])
            size = self.SIZE_TO_E[int(command[2])]
            self.system.stage.relative(pos, size)
        elif op in self.ABSOLUTE:
            assert len(command) == 2 or len(command) == 3
            pos = int(command[1])
            size = 2
            if len(command) == 3:
                size = int(command[2])
            self.system.stage.absolute(pos, self.SIZE_TO_E[size])
        elif op in self.SPEED:
            assert len(command) == 2
            hz = int(command[1])
            self.system.stage.speed(hz)
        elif op in self.CANCEL:
            self.system.stage.stop()
        elif op in self.HOME:
            assert len(command) == 2 or len(command) == 3
            assert command[1] in ("-", "+")
            size = 8
            if len(command) == 3:
                size = int(command[2])
            self.system.stage.home(StageDirection.FORWARD if command[1] == "+" else StageDirection.BACKWARD,
                                   self.SIZE_TO_E[size])
        elif op in self.SET_POSITION:
            assert len(command) == 2
            pos = int(command[1])
            self.system.stage.set_position(pos)
        elif op in self.GET_POSITION:
            print(f"Position: {self.system.stage.get_position()}")
        elif op in self.LED_PWM:
            assert len(command) == 2
            self.system.stage.led_pwm(float(command[1]))
        elif op in self.LED_VOLTAGE:
            assert len(command) == 2
            self.system.stage.led_voltage(float(command[1]))
        elif op in self.LED_KP:
            assert len(command) == 2
            self.system.stage.led_pid_p(float(command[1]))
        elif op in self.LED_KI:
            assert len(command) == 2
            self.system.stage.led_pid_i(float(command[1]))
        elif op in self.LED_KD:
            assert len(command) == 2
            self.system.stage.led_pid_d(float(command[1]))
        elif op in self.DEBOUNCE:
            assert len(command) == 2
            self.system.stage.switch_debounce(int(command[1]))
        elif op in self.SLEEP:
            assert len(command) == 2
            time.sleep(float(command[1]))
        elif op in self.RUN:
            assert len(command) >= 2
            cmd = self.system.__getattribute__(command[1])
            if len(command) > 2:
                ret = cmd(*command[2:])
            else:
                ret = cmd()
            if ret:
                print(ret)
        elif op in self.HELP:
            print("i: idle packet (show status flags)\n"
                  "w [timeout = 0.0s] [granularity = 0.1s]: wait for a motor request to finish\n"
                  "r [pos] [1,2,4,8]: relative motion with step size\n"
                  "a [pos] [1,2,4,8]?: Absolute motion to position\n"
                  "c: Cancel a running motor request\n"
                  "h [+,-] [1,2,4,8]?: Home the stage to one of the limit switches\n"
                  "s [hz]: Set the motor step rate in hertz\n"
                  "sp [pos]: Set the current position to pos\n"
                  "gp -> pos: Get the current position of stage\n"
                  "pwm [0.0 - 1.0]: Set the ring light's pwm level\n"
                  "v [0.0v - 3.3v]: Control the ring light level using voltage on the photo-transistor\n"
                  "kp [kp]: Set voltage Kp value\n"
                  "ki [ki]: Set voltage Ki value\n"
                  "kd [kd]: Set voltage Kd value\n"
                  "d [delay ms]: Set the debounce delay on the motor \n"
                  "?: show this help message\n"
                  "q: quit the program\n"
                  "clear: clear the terminal screen\n"
                  "sleep [seconds]: wait for a certain amount of time\n",
                  "run [script] args...\n"
                  )
        elif op in self.QUIT:
            print("Exiting")
            exit(0)
        elif op in self.CLEAR:
            os.system("clear")
        else:
            print(f"Unknown command '{command[0]}'")


def create_system(args) -> System:
    if len(args) >= 2:
        ser = serial.Serial(args[1], 115200, timeout=1.0)
        stage = Stage(ser)
    else:
        stage = Stage(None)

    hq_cam = -1
    aux_cam = -1
    if len(args) >= 3:
        hq_cam = int(args[2])
    if len(args) >= 4:
        aux_cam = int(args[3])

    return System(stage, HqCamera(hq_cam), AuxCamera(aux_cam))


def main(args):
    cli = Cli(create_system(args))

    while True:
        try:
            command = input("> ")
        except KeyboardInterrupt:
            print("^C")
            continue
        except EOFError:
            print()
            break

        try:
            cli.execute(Cli.parse(command))
        except KeyboardInterrupt:
            continue
        except Exception:
            traceback.print_exc()

    return 0


if __name__ == "__main__":
    import sys

    exit(main(sys.argv))
