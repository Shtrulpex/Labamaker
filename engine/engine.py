from data.data import *
from data_processing.data_processing import *
from visualization.visualization import *


class Laba:
    def __init__(self, data_controller: DataController):
        self.data = data_controller

    def make_laba(self):
        pass

    def get_userdata(self):
        return self.data.source.get_tables()


class Laba226(Laba):
    def make_laba(self):
        table1 = self.data.source.get_tables('d2mm')  #трубка d = 3 мм
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
