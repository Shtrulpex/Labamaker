from data.data import *
from data_processing.data_processing import *
from visualization.visualization import *
from math import pi


class Laba:
    def __init__(self, data_controller: DataController):
        self.data = data_controller

    def make_laba(self):
        pass

    def get_userdata(self):
        return self.data.source.get_tables()


class Laba226(Laba):
    def make_laba(self):
        table1 = self.data.source.get_tables('d2mm')  # трубка d = 3 мм
        q = np.array([])
        for i in range(len(table1.dV)):
            np.append(q, Division({Data.X: table1.dV[i], Data.Y: table1.dt[i]}).calc())
        table1['q'] = q
        table1.to_csv('d2mm')
        self.data.result.add_table('d2mm')
        mls_args = MLS({Data.X: table1.q, Data.Y: table1.dp})
        fig = Visualizator.illustrate(mls_args, GraphType.MLS)
        fig.savefig('q(dp)_d2mm.pdf')
        self.data.result.add_image('q(dp)_d2mm.pdf')


class Laba111(Laba):
    def make_laba(self):
        params = self.data.source.get_parameters()
        tables = self.data.source.get_tables()
        resistance_table = 0
        for i in tables:
            if i.get_name() == 'measure_1':
                resistance_table = i
                break

        mls_args = MLS({Data.X: np.array(resistance_table.get_table().N),
                        Data.Y: np.array(resistance_table.get_table().R)}).calc()
        figure = Visualizator.illustrate(mls_args, GraphType.MLS)
        self.data.result.add_image(figure)
        self.data.result.add_parameter(mls_args[Data.K])
        self.data.result.add_parameter(mls_args[Data.B])
        self.data.result.add_parameter(mls_args[Data.DK])
        self.data.result.add_parameter(mls_args[Data.DB])
        s = params[0] * params[0] * 0.25 * pi
        l = params[1] * pi

        step = params[2] / params[3]

        l = l * l + step * step
        l = l ** 0.5

        p = Division({Data.X: [mls_args[Data.K], s], Data.Y: [l]}).calc()
        l.set_symbol('l')
        l.set_name('one_circle_length')
        step.set_symbol('Δ')
        step.set_name('step')
        p[Data.RESULT].set_symbol('ρ')
        p[Data.RESULT].set_name('resistivity')
        self.data.result.add_parameter(step)
        self.data.result.add_parameter(l)
        self.data.result.add_parameter(p[Data.RESULT])

        # кинуть итоги мнк в параметры резалта
