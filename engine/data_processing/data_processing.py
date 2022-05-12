import numpy as np
from enum import Enum, auto


class Data(Enum):
    X = auto()
    Y = auto()
    K = auto()
    B = auto()
    DK = auto()
    DB = auto()


class Method:
    def __init__(self, result, arguments, sequence):
        self.result = result
        self.args = arguments
        self.sequence = sequence

    def calc(self):
        pass


class CalcData:
    @staticmethod
    def do(d):
        return {Data.X: [1, 2, 3, 4, 5], Data.Y:[1, 2,3,4,5]}
    # парсит на x и y, но хз как


class CalcK(CalcData):
    @staticmethod
    def do(d):
        a = np.vstack([d[Data.X], np.ones(len(d[Data.X]))]).T
        k, b = np.linalg.lstsq(a, d[Data.Y], rcond=None)[0]
        d[Data.K] = k
        return d


class CalcB(CalcData):
    @staticmethod
    def do(d):
        a = np.vstack([d[Data.X], np.ones(len(d[Data.X]))]).T
        k, b = np.linalg.lstsq(a, d[Data.Y], rcond=None)[0]
        d[Data.B] = b
        return d


class CalcDK(CalcData):
    @staticmethod
    def do(d):
        x_2 = np.array(d[Data.X]).mean() ** 2
        y_2 = np.array(d[Data.Y]).mean() ** 2
        x2_ = (np.array(d[Data.X]) ** 2).mean()
        y2_ = (np.array(d[Data.Y]) ** 2).mean()
        dk = (y2_ - y_2) / (x2_ - x_2) - np.array(d[Data.B]) ** 2
        dk **= 0.5
        dk /= len(d[Data.X]) ** 0.5
        d[Data.DK] = dk
        return d


class CalcDB(CalcData):
    @staticmethod
    def do(d):
        x_2 = np.array(d[Data.X]).mean() ** 2
        x2_ = (np.array(d[Data.X]) ** 2).mean()
        d[Data.DB] = d[Data.DK] * (x2_ - x_2) ** 0.5
        return d


class MLS(Method):
    def __init__(self, arguments):
        super().__init__(CalcData.do(arguments), arguments, [CalcData, CalcK, CalcB, CalcDK, CalcDB])

    def calc(self):
        for i in self.sequence:
            self.result = i.do(self.result)
        return self.result