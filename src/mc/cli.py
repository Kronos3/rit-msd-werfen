import serial

from mc.stage import Stage, StageStepSize


def main(args):
    assert len(args) == 2, f"Expecting only serial port argument"

    ser = serial.Serial(args[1], 115200)
    stage = Stage(ser)

    size_to_e = {
        1: StageStepSize.FULL,
        2: StageStepSize.HALF,
        4: StageStepSize.QUARTER,
        8: StageStepSize.EIGHTH,
    }

    while True:
        try:
            command = input("> ").split(" ")
        except KeyboardInterrupt:
            continue
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
                assert len(command) == 3
                pos = int(command[1])
                size = size_to_e[int(command[2])]
                stage.relative(pos, size)
            elif op == "a":
                assert len(command) == 2
                pos = int(command[1])
                stage.absolute(pos)
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
            else:
                print(f"Unknown command '{command[0]}'")
        except AssertionError as e:
            print(e)

    return 0


if __name__ == "__main__":
    import sys
    exit(main(sys.argv))
