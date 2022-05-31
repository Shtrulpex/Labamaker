import numpy as np
from math import pi
from engine.enums import *


class Method:
    def __init__(self, result, arguments, sequence):
        self.__result = result
        self.__args = arguments
        self.__sequence = sequence

    def do(self):
        for i in self.__sequence:
            self.__result = i.do(self.__result)
        return self.__result


class CalcData:
    @staticmethod
    def do(d):
        return d


class CalcK(CalcData):
    @staticmethod
    def do(d):
        xy_ = (d[Data.X] * d[Data.Y]).mean()
        x_ = d[Data.X].mean()
        y_ = d[Data.Y].mean()
        k = xy_ - x_ * y_
        x2_ = (d[Data.X] ** 2).mean()
        x_2 = (d[Data.X]).mean() ** 2
        k = k / (x2_ - x_2)
        k.set_symbol('k')
        k.set_name('mls_koef_k')
        d[Data.K] = k
        return d


class CalcB(CalcData):
    @staticmethod
    def do(d):
        y_ = d[Data.Y].mean()
        x_ = d[Data.X].mean()
        b = y_ - d[Data.K] * x_
        b.set_symbol('b')
        b.set_name('mls_koef_b')
        d[Data.B] = b
        return d


class CalcDK(CalcData):
    @staticmethod
    def do(d):
        x_2 = (d[Data.X]).mean() ** 2
        y_2 = (d[Data.Y]).mean() ** 2
        x2_ = (d[Data.X] ** 2).mean()
        y2_ = (d[Data.Y] ** 2).mean()
        dk = (y2_ - y_2) / (x2_ - x_2) - d[Data.B] ** 2
        dk = dk ** 0.5
        dk = dk / (len(d[Data.X]) ** 0.5)
        d[Data.DK] = dk
        dk.set_symbol('dk')
        dk.set_name('k_error')
        return d


class CalcDB(CalcData):
    @staticmethod
    def do(d):
        x_2 = np.array(d[Data.X]).mean() ** 2
        x2_ = (np.array(d[Data.X]) ** 2).mean()
        db = d[Data.DK] * (x2_ - x_2) ** 0.5
        db.set_symbol('db')
        db.set_name('b_error')
        d[Data.DB] = db
        return d


class Divide(CalcData):
    @staticmethod
    def do(d):
        x = 1
        y = 1
        for i in d[Data.X]:
            x = i * x
        for i in d[Data.Y]:
            y = i * y
        d[Data.RESULT] = x / y
        return d


class CalcCircleSquare(CalcData):
    @staticmethod
    def do(d):
        s = d[Data.d] ** 2 * pi * 0.25
        s.set_symbol('S')
        s.set_name('circle_square')
        d[Data.S] = s
        return d


class CalcStep(CalcData):
    @staticmethod
    def do(d):
        step = d[Data.L] / (d[Data.N]-d[Data.N]/d[Data.N])
        step.set_symbol('Δ')
        step.set_name('step')
        d[Data.STEP] = step
        return d


class CalcCircleL(CalcData):
    @staticmethod
    def do(d):
        l = (d[Data.D] - d[Data.h] * 2) * pi
        l.set_symbol('l')
        l.set_name('circle_length')
        d[Data.lc] = l
        l.set_symbol('lc')
        l.set_name('circle_length')
        return d


class CalcCirclenStep(CalcData):
    @staticmethod
    def do(d):
        l = d[Data.lc] ** 2 + d[Data.STEP] ** 2
        l = l ** 0.5
        l.set_symbol('l')
        l.set_name('circle_length_with_step')
        d[Data.l] = l
        return d


class CalcResistivity(CalcData):
    @staticmethod
    def do(d):
        p = d[Data.K] * d[Data.S] / d[Data.l]
        p.set_symbol('ρ')
        p.set_name('resistivity')
        d[Data.P] = p
        return d


class MLS(Method):
    def __init__(self, arguments):
        super().__init__(CalcData.do(arguments), arguments, [CalcData, CalcK, CalcB, CalcDK, CalcDB])


class Division(Method):
    def __init__(self, arguments):
        super().__init__(CalcData.do(arguments), arguments, [CalcData, Divide])


class Resistivity(Method):
    def __init__(self, arguments, circle_wire=True, use_mls=True):
        super().__init__(CalcData.do(arguments), arguments, [CalcData, CalcK, CalcCircleSquare, CalcStep, CalcCircleL, CalcCirclenStep, CalcResistivity])
