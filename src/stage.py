import enum


class StageOpcode(enum.IntEnum):
    IDLE = 0
    RELATIVE = 1
    ABSOLUTE = 2
    SET = 3
    HOME = 4
    GET_POSITION = 5


class StagePacket:
    opcode: StageOpcode
    arg1: int
    arg2: int
    flags: int

    def __init__(self, opcode: StageOpcode,
                 arg1: int = 0, arg2: int = 0,
                 flags: int = 0):
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        self.flags = flags

    def encode(self) -> bytes:

