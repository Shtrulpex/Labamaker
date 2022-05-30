import os
from matplotlib.pyplot import figure as fig

from engine.data.table import *


class Data:
    def __init__(self, folder: str):
        self._folder = folder
        self._tables = []  # list of tables:
        self._parameters = []  # list of parameters

    def get_tables(self):
        return self._tables

    def get_parameters(self):
        return self._parameters

    def folder(self):
        return self._folder

    def table_folder(self):  # returns path to tables
        return f'{self.folder()}\\tables'

    def parameter_folder(self):   # returns path to tables
        return f'{self.folder()}\\parameters'

    def add_table(self, table_: Table):
        self._tables.append(table_)
        table_.to_csv(self.table_folder())

    def add_parameter(self, parameter: Parameter):
        self._parameters.append(parameter)
        parameter.to_json(self.parameter_folder())

    def _read_tables(self):
        path = self.table_folder()
        files = os.listdir(path=path)
        current_directory = os.getcwd()
        os.chdir(path)
        for file in files:
            if not file.endswith('.json'):
                continue
            with open(file, 'r', encoding='utf8') as f:
                data = json.load(f)
            for name in data.keys():
                self._tables.append(
                    Table.init_from_file(name, data[name])
                )
        os.chdir(current_directory)

    def _read_parameters(self):
        path = self.parameter_folder()
        files = os.listdir(path=path)
        current_directory = os.getcwd()
        os.chdir(path)
        for file in files:
            with open(file, 'r', encoding='utf8') as f:
                data = json.load(f)
            for name in data.keys():
                self._parameters.append(
                    Parameter.init_from_file(name, data[name])
                )
        os.chdir(current_directory)


class DataSource(Data):
    def __init__(self, folder: str):
        super(DataSource, self).__init__(folder)
        self._read_tables()
        self._read_parameters()


class DataResult(Data):
    def __init__(self, folder: str):
        super().__init__(folder)
        self._images = []
        self._texts = []
        self.__read_texts()

    def image_folder(self):
        return f'{self.folder()}\\images'

    def get_images(self):
        return self._images

    def add_image(self, image: fig):
        pass

    def __read_texts(self):
        pass


class DataMaterial(Data):
    def __init__(self, folder: str):
        super(DataMaterial, self).__init__(folder)
        self._read_tables()
        self._read_parameters()


class DataController:
    def __init__(self, lab: str):
        self.lab = lab
        self.__generate_data()

    def __generate_data(self):
        source_folder = f'..\\..\\sources\\{self.lab}'
        self.source = DataSource(source_folder)

        material_folder = f'..\\..\\materials\\{self.lab}'
        self.material = DataMaterial(material_folder)

        result_folder = f'..\\..\\results\\{self.lab}'
        self.result: DataResult = DataResult(result_folder)


dc = DataController('lab_111')
d = dc.material.get_parameters()[0]
D = dc.material.get_parameters()[1]
N = dc.material.get_parameters()[3]
print(d)
print(D)
print(N)
dDd = d * D * d
print(dDd)
dDd >> 3
print(dDd)
unit = dDd.get_unit_numerator()[0]
dDd.set_prefix(unit, 'm')
print(dDd)
dDd.set_prefix(unit, 'M')
print(dDd)
dDd << 2
print(dDd)
print(d)
print(D)
DN = N / D ** 2
DN >> 5
print(DN)
k = N / 5
print(k)
print('All is good')


# testing Tables:
table = dc.source.get_tables()[0]

print(table)
print(table.keys())
table['R_ev'] = d
table['R'][3] = D
table['R_ev'][3] *= 2
table['R_ev'] *= table['R'][3]
print(table)
print()
print(table.iloc[2])
print()


table1 = dc.material.get_tables()[0]
print(table1)
table1.insert(2, '12321', table['R_ev'])
print(table1)

print('All is good')
