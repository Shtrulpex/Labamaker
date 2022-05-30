


class Method:
    def __init__(self, result, arguments, sequence):
        self.result = result
        self.args = arguments
        self.sequence = sequence

    def calc(self):
        for i in self.sequence:
            self.result = i.do(self.result)
        return self.result


class CalcData:
    @staticmethod
    def do(d):
        return d


class CalcK(CalcData):
    @staticmethod
    def do(d):
        xy_ = (d[Data.X] * d[Data.Y]).mean()
        x_ = d[Data.X].mean()
        y_ = d(Data.Y).mean()
        k = xy_ - x_ * y_
        y2_ = (d[Data.Y] ** 2).mean()
        y_2 = (d[Data.Y]).mean() ** 2
        k = k / (y2_ - y_2)
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
        dk = dk / len(d[Data.X]) ** 0.5
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
            x = x * i
        for i in d[Data.Y]:
            y = y * i
        d[Data.RESULT] = x / y
        return d


class MLS(Method):
    def __init__(self, arguments):
        super().__init__(CalcData.do(arguments), arguments, [CalcData, CalcK, CalcB, CalcDK, CalcDB])


class Division(Method):
    def __init__(self, arguments):
        super().__init__(CalcData.do(arguments), arguments, [CalcData, Divide])
