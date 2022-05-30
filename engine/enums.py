from enum import Enum, auto


class Data(Enum):
    X = auto()
    Y = auto()
    K = auto()
    B = auto()
    DK = auto()
    DB = auto()
    RESULT = auto()


class GraphType(Enum):
    MLS = auto()
    BAR = auto()