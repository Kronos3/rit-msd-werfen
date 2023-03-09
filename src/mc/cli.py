import os
import traceback
import readline
from typing import List

import serial

from stage import Stage, StageStepSize, StageDirection


class Commands:
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


SIZE_TO_E = {
    1: StageStepSize.FULL,
    2: StageStepSize.HALF,
    4: StageStepSize.QUARTER,
    8: StageStepSize.EIGHTH,
}


def execute_command(stage: Stage, command: List[str]):
    op = command[0]
    if not op:
        return

    if op in Commands.IDLE:
        stage.idle()
        print(f"LIMIT 1: {'ON' if stage.limit_1 else 'OFF'}\n"
              f"LIMIT 2: {'ON' if stage.limit_2 else 'OFF'}\n"
              f"E-STOP: {'ON' if stage.estop else 'OFF'}\n"
              f"RUNNING: {'ON' if stage.running else 'OFF'}\n"
              f"LED: {'ON' if stage.led else 'OFF'}")
    elif op in Commands.WAIT:
        assert len(command) <= 3, command
        timeout = 0.0
        granularity = 0.1
        if len(command) >= 2:
            timeout = float(command[1])
        if len(command) == 3:
            granularity = float(command[2])
        stage.wait(timeout, granularity)
    elif op in Commands.RELATIVE:
        assert len(command) == 3, command
        pos = int(command[1])
        size = SIZE_TO_E[int(command[2])]
        stage.relative(pos, size)
    elif op in Commands.ABSOLUTE:
        assert len(command) == 2 or len(command) == 3
        pos = int(command[1])
        size = 2
        if len(command) == 3:
            size = int(command[2])
        stage.absolute(pos, SIZE_TO_E[size])
    elif op in Commands.SPEED:
        assert len(command) == 2
        hz = int(command[1])
        stage.speed(hz)
    elif op in Commands.CANCEL:
        stage.stop()
    elif op in Commands.HELP:
        assert len(command) == 2 or len(command) == 3
        assert command[1] in ("-", "+")
        size = 8
        if len(command) == 3:
            size = int(command[2])
        stage.home(StageDirection.FORWARD if command[1] == "+" else StageDirection.BACKWARD,
                   SIZE_TO_E[size])
    elif op in Commands.SET_POSITION:
        assert len(command) == 2
        pos = int(command[1])
        stage.set_position(pos)
    elif op in Commands.GET_POSITION:
        print(f"Position: {stage.get_position()}")
    elif op in Commands.LED_PWM:
        assert len(command) == 2
        stage.led_pwm(float(command[1]))
    elif op in Commands.LED_VOLTAGE:
        assert len(command) == 2
        stage.led_voltage(float(command[1]))
    elif op in Commands.LED_KP:
        assert len(command) == 2
        stage.led_pid_p(float(command[1]))
    elif op in Commands.LED_KI:
        assert len(command) == 2
        stage.led_pid_i(float(command[1]))
    elif op in Commands.LED_KD:
        assert len(command) == 2
        stage.led_pid_d(float(command[1]))
    elif op in Commands.DEBOUNCE:
        assert len(command) == 2
        stage.switch_debounce(int(command[1]))
    elif op in Commands.HELP:
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
              )
    elif op in Commands.QUIT:
        print("Exiting")
        exit(0)
    elif op in Commands.CLEAR:
        os.system("clear")
    else:
        print(f"Unknown command '{command[0]}'")


def main(args):
    assert len(args) == 2, f"Expecting only serial port argument"

    ser = serial.Serial(args[1], 115200, timeout=1.0)
    stage = Stage(ser)

    while True:
        try:
            command = input("> ").strip().split(" ")
        except KeyboardInterrupt:
            print("^C")
            continue
        except EOFError:
            print()
            break

        try:
            execute_command(stage, command)
        except Exception:
            traceback.print_exc()

    return 0


if __name__ == "__main__":
    import sys
    exit(main(sys.argv))
