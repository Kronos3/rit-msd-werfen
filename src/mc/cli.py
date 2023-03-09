import traceback
import readline

import serial
from stage import Stage
from system import System


def main(args):
    assert len(args) == 2, f"Expecting only serial port argument"

    ser = serial.Serial(args[1], 115200, timeout=1.0)
    stage = Stage(ser)
    system = System(stage)

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
            system.execute(System.parse(command))
        except Exception:
            traceback.print_exc()

    return 0


if __name__ == "__main__":
    import sys
    exit(main(sys.argv))
