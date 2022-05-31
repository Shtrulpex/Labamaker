import numpy as np
import matplotlib.pyplot as plt
from engine.enums import *


class Visualizator:
    @staticmethod
    def illustrate(arguments, graph_type):
        if graph_type == GraphType.MLS:
            return MLSLine(arguments).get_graph()


class Graph:
    def __init__(self, arguments, size_x=20, size_y=20, dpi=300):
        self.size_x = size_x
        self.size_y = size_y
        self.args = arguments
        self.dpi = dpi

    def get_graph(self):
        pass


class MLSLine(Graph):
    def __init__(self, arguments, size_x=20, size_y=20, dpi=300, grid=True):
        super().__init__(arguments, size_x, size_y, dpi)
        self.grid = grid

    def get_graph(self):
        fig, ax = plt.subplots(1, 1, figsize=(self.size_x, self.size_y), dpi=self.dpi)
        if self.grid:
            ax.grid()
        x = np.array(list(map(lambda x: x.get_number(), self.args[Data.X])))
        y = np.array(list(map(lambda x: x.get_number(), self.args[Data.Y])))
        k = self.args[Data.K].get_number()
        b = self.args[Data.B].get_number()
        ax.plot(x, k*x + b)
        ax.scatter(x, y)
        return fig
