from engine.data.data import *
from engine.output.output import *
from engine.data_processing.data_processing import *
from engine.visualization.visualization import *


class Lab:
    def __init__(self, data_controller: DataController):
        self.dc = data_controller

    def make_lab(self):
        pass

    def get_userdata(self):
        return self.dc.source.get_tables()

    def end_lab(self):
        self.dc.result.write_json()
        self.__prepare_data()
        self.dc.result.write_pdf()

    def _add_params(self, *params):
        for i in params:
            self.dc.result.add_parameter(i)

    def _add_tables(self, *tables):
        for i in tables:
            self.dc.result.add_table(i)

    def __prepare_data(self):
        self._add_params(*self.dc.material.get_parameters())
        self._add_tables(*self.dc.material.get_tables())


class Lab111(Lab):
    def __init__(self):
        dc = DataController('lab_111')
        super(Lab111, self).__init__(dc)

    def make_lab(self):
        params = self.dc.material.get_parameters()
        tables = self.dc.material.get_tables()
        resistance_table = tables[0]
        for i in tables:
            if i.name() == 'measures_1':
                resistance_table = i
                break

        mls_args = MLS({Data.X: resistance_table['N'].to_numpy(),
                        Data.Y: resistance_table['R'].to_numpy()}).do()
        figure = Visualizator.illustrate(mls_args, GraphType.MLS)
        self.dc.result.add_image(figure)
        self._add_params(mls_args[Data.K], mls_args[Data.B], mls_args[Data.DK], mls_args[Data.DB])

        p = {Data.X: resistance_table['N'].to_numpy(),
             Data.Y: resistance_table['R'].to_numpy(),
             Data.h: params[5],
             Data.d: params[0],
             Data.L: params[2],
             Data.N: params[3],
             Data.D: params[1]}
        p = Resistivity(p).do()
        self._add_params(p[Data.S], p[Data.lc], p[Data.STEP], p[Data.l], p[Data.P])

        for i in self.dc.result.get_parameters():
            print(i)
        self.end_lab()
