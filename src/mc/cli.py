import traceback
import readline
import serial

from stage import Stage, StageStepSize, StageDirection


def main(args):
    assert len(args) == 2, f"Expecting only serial port argument"

    ser = serial.Serial(args[1], 115200, timeout=1.0)
    stage = Stage(ser)

    size_to_e = {
        1: StageStepSize.FULL,
        2: StageStepSize.HALF,
        4: StageStepSize.QUARTER,
        8: StageStepSize.EIGHTH,
    }

    while True:
        try:
            command = input("> ").strip().split(" ")
        except KeyboardInterrupt:
            break
        except EOFError:
            break

        try:
            op = command[0]
            if op == "i":
                stage.idle()
                print(f"LIMIT 1: {'ON' if stage.limit_1 else 'OFF'}\n"
                      f"LIMIT 2: {'ON' if stage.limit_2 else 'OFF'}\n"
                      f"E-STOP: {'ON' if stage.estop else 'OFF'}\n"
                      f"LED: {'ON' if stage.led else 'OFF'}")
            elif op == "r":
                assert len(command) == 3, command
                pos = int(command[1])
                size = size_to_e[int(command[2])]
                stage.relative(pos, size)
            elif op == "a":
                assert len(command) == 2 or len(command) == 3
                pos = int(command[1])
                size = 2
                if len(command) == 3:
                    size = int(command[2])
                stage.absolute(pos, size_to_e[size])
            elif op == "h":
                assert len(command) == 2
                assert command[1] in ("-", "+")
                stage.home(StageDirection.FORWARD if command[1] == "+" else StageDirection.BACKWARD)
            elif op == "sp":
                assert len(command) == 2
                pos = int(command[1])
                stage.set_position(pos)
            elif op == "gp":
                print(f"Position: {stage.get_position()}")
            elif op == "pwm":
                assert len(command) == 2
                stage.led_pwm(float(command[1]))
            elif op == "v":
                assert len(command) == 2
                stage.led_voltage(float(command[1]))
            elif op == "kp":
                assert len(command) == 2
                stage.led_pid_p(float(command[1]))
            elif op == "ki":
                assert len(command) == 2
                stage.led_pid_i(float(command[1]))
            elif op == "kd":
                assert len(command) == 2
                stage.led_pid_d(float(command[1]))
            elif op == "?":
                print("i: idle packet (show status flags)\n"
                      "r [pos] [1,2,4,8]: relative motion with step size\n"
                      "a [pos] [1,2,4,8]?: Absolute motion to position\n"
                      "h [+,-]: Home the stage to one of the limit switches\n"
                      "sp [pos]: Set the current position to pos\n"
                      "gp -> pos: Get the current position of stage\n"
                      "pwm [0.0% - 1.0%]: Set the ring light's pwm level\n"
                      "v [0.0v - 3.3v]: Control the ring light level using voltage on the photo-transistor\n"
                      "kp: Set voltage Kp value\n"
                      "ki: Set voltage Ki value\n"
                      "kd: Set voltage Kd value\n"
                      "?: show this help message"
                      )
            elif op == "q":
                print("Exiting")
                break
            else:
                print(f"Unknown command '{command[0]}'")
        except Exception:
            traceback.print_exc()

    return 0


if __name__ == "__main__":
    import sys
    exit(main(sys.argv))
