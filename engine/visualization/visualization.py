import numpy as np
import matplotlib.pyplot as plt
from enum import Enum, auto

# надо будет удалить(это тот же data что и в data_proc)
class Data(Enum):
    X = auto()
    Y = auto()
    K = auto()
    B = auto()
    DK = auto()
    DB = auto()


class GraphType(Enum):
    MLS = auto()
    BAR = auto()


class Visualizator:
    @staticmethod
    def illustrate(arguments, graph_type):
        if graph_type == GraphType.MLS:
            return MLS(arguments).get_graph()


class Graph:
    def __init__(self, arguments, size_x=20, size_y=20, dpi=300):
        self.size_x = size_x
        self.size_y = size_y
        self.args = arguments
        self.dpi = dpi

    def get_graph(self):
        pass


class MLS(Graph):
    def __init__(self, arguments, size_x=20, size_y=20, dpi=300, grid=True):
        super().__init__(arguments, size_x, size_y, dpi)
        self.grid = grid

    def get_graph(self):
        fig, ax = plt.subplots(1, 1, figsize=(self.size_x, self.size_y), dpi=self.dpi)
        if self.grid:
            ax.grid()
        x = np.array(self.args[Data.X])
        y = np.array(self.args[Data.Y])
        k = np.array(self.args[Data.K])
        b = np.array(self.args[Data.B])
        ax.plot(x, k*x + b)
        ax.scatter(x, y)
        fig.savefig('MLS1.pdf')
        return fig
