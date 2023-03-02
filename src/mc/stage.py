import enum
import struct
import serial

from crc import crc8


class StageOpcode(enum.IntEnum):
    IDLE = 0
    RELATIVE = 1
    ABSOLUTE = 2
    HOME = 3
    SET_POSITION = 4
    GET_POSITION = 5
    LED_PWM = 6,
    LED_VOLTAGE = 7,
    LED_PID = 8,


class StageDirection(enum.IntEnum):
    FORWARD = 0
    BACKWARD = 1


class StageFlags(enum.IntFlag):
    PID_P = 0
    PID_I = 1
    PID_D = 2

    LIMIT_1 = 1 << 0
    LIMIT_2 = 1 << 1
    ESTOP = 1 << 2
    RUNNING = 1 << 3
    LED = 1 << 4


class StageStepSize(enum.IntEnum):
    FULL = 0
    HALF = 1
    QUARTER = 2
    EIGHTH = 3


class StagePacket:
    opcode: StageOpcode
    arg: int | float
    flags: int

    def __init__(self, opcode: StageOpcode,
                 arg: int | float = 0,
                 flags: int = 0):
        self.opcode = opcode
        self.arg = arg
        self.flags = flags

    def encode(self) -> bytes:
        packet_start = struct.pack(
            f"<BBH{'i' if type(self.arg) is int else 'f'}B",
            0xDE, 0xAD,
            self.opcode,
            self.arg,
            self.flags)

        return packet_start + struct.pack(
            "BBB", crc8(packet_start), 0xBE, 0xEF)

    @staticmethod
    def decode(m: bytes) -> 'StagePacket':
        assert len(m) == 12, len(m)

        s1, s2, opcode, arg, flags, xsum, e1, e2 = struct.unpack("BBHiBBBB", m)

        assert s1 == 0xDE and s2 == 0xAD, (hex(s1), hex(s2))
        assert e1 == 0xBE and e2 == 0xEF, (hex(e1), hex(e2))

        calculated_crc = crc8(m[:9])
        assert calculated_crc == xsum, (calculated_crc, xsum)

        return StagePacket(opcode, arg, flags)


class Stage:
    limit_1: bool
    limit_2: bool
    estop: bool
    running: bool
    led: bool

    def __init__(self, ser: serial.Serial):
        self.serial = ser

        self.limit_1 = False
        self.limit_2 = False
        self.estop = False
        self.running = False
        self.led = False

    def send(self, pkt: StagePacket):
        self.serial.write(pkt)

        reply_bytes = self.serial.read(12)
        reply = StagePacket.decode(reply_bytes)

        self.limit_1 = bool(StageFlags.LIMIT_1 & reply.flags)
        self.limit_2 = bool(StageFlags.LIMIT_2 & reply.flags)
        self.estop = bool(StageFlags.ESTOP & reply.flags)
        self.running = bool(StageFlags.RUNNING & reply.flags)
        self.led = bool(StageFlags.LED & reply.flags)

        return reply

    def idle(self):
        """
        Send an idle packet to the stage
        This is used to update the status flags periodically
        """
        self.send(StagePacket(StageOpcode.IDLE))

    def relative(self, n: int, size: StageStepSize):
        """
        Perform a relative motion
        :param n: number of steps
        :param size: size of the stage steps
        """
        pkt = StagePacket(
            StageOpcode.RELATIVE,
            abs(n),
            (size & 0x0F) | (0xF0 if n < 0 else 0x00)
        )

        self.send(pkt)

    def absolute(self, n: int):
        pkt = StagePacket(StageOpcode.ABSOLUTE, abs(n))
        self.send(pkt)

    def home(self, direction: StageDirection):
        # Full throttle to one of the edges
        # Stops when it hits a limit switch or ESTOP
        if direction == StageDirection.FORWARD:
            self.relative(100000, StageStepSize.FULL)
        else:
            self.relative(-100000, StageStepSize.FULL)

    def set_position(self, pos: int):
        self.send(StagePacket(StageOpcode.SET_POSITION, pos))

    def get_position(self) -> int:
        reply = self.send(StagePacket(StageOpcode.GET_POSITION))
        return reply.arg

    def led_pwm(self, pwm: float):
        assert 0.0 <= pwm <= 1.0, pwm
        self.send(StagePacket(StageOpcode.LED_PWM, pwm))

    def led_voltage(self, voltage: float):
        assert 0.0 <= voltage <= 3.3, f"Voltage must between 0V and 3.3V: {round(voltage, 2)}V"
        self.send(StagePacket(StageOpcode.LED_VOLTAGE, voltage))

    def led_pid_p(self, kp: float):
        self.send(StagePacket(StageOpcode.LED_PID, kp, StageFlags.PID_P))

    def led_pid_i(self, ki: float):
        self.send(StagePacket(StageOpcode.LED_PID, ki, StageFlags.PID_I))

    def led_pid_d(self, kd: float):
        self.send(StagePacket(StageOpcode.LED_PID, kd, StageFlags.PID_D))
