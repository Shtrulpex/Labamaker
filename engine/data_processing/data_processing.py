import numpy as np


class Method:
    def __init__(self, result, arguments):
        self.result = result
        self.args = arguments


class MLS(Method):
    def do(self):
        x = self.args['x']
        y = self.args['y']
        a = np.vstack([x, np.ones(len(x))]).T
        k, b = np.linalg.lstsq(a, y, rcond=None)[0]
        x_2 = x.mean()**2
        y_2 = y.mean()**2
        x2_ = (x**2).mean()
        y2_ = (y**2).mean()
        dk = (y2_-y_2)/(x2_-x_2) - b**2
        dk **= 0.5
        dk /= len(x)**0.5
        db = dk * (x2_ - x_2)**0.5
        self.result = {'k': k, 'b': b, 'dk': dk, 'db': db}
        return self.result

