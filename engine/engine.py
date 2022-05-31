from engine.data.data import *
from engine.data_processing.data_processing import *
from engine.visualization.visualization import *


class Lab:
    def __init__(self, data_controller: DataController):
        self.data = data_controller

    def make_lab(self):
        pass

    def get_userdata(self):
        return self.data.source.get_tables()

    def add_params(self, *params):
        for i in params:
            self.data.result.add_parameter(i)


class Lab111(Lab):
    def make_lab(self):
        params = self.data.material.get_parameters()
        tables = self.data.material.get_tables()
        resistance_table = tables[0]
        for i in tables:
            if i.name() == 'measures_1':
                resistance_table = i
                break

        mls_args = MLS({Data.X: resistance_table['N'].to_numpy(),
                        Data.Y: resistance_table['R'].to_numpy()}).do()
        figure = Visualizator.illustrate(mls_args, GraphType.MLS)
        self.data.result.add_image(figure)
        self.add_params(mls_args[Data.K], mls_args[Data.B], mls_args[Data.DK], mls_args[Data.DB])

        p = {Data.X: resistance_table['N'].to_numpy(),
             Data.Y: resistance_table['R'].to_numpy(),
             Data.d: params[0],
             Data.L: params[2],
             Data.N: params[3],
             Data.D: params[1]}
        p = Resistivity(p).do()
        self.add_params(p[Data.S], p[Data.STEP], p[Data.l], p[Data.P])

        for i in self.data.result.get_parameters():
            print(i)
        self.data.result.end()