from matplotlib.pyplot import figure as fig
import json
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
        return f'{self.folder()}/tables'

    def parameter_folder(self):   # returns path to tables
        return f'{self.folder()}/parameters'

    def add_table(self, table_: Table):
        self._tables.append(table_)
        table_.to_csv(self.table_folder())

    def add_parameter(self, parameter: Parameter):
        self._parameters.append(parameter)

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
        self.__read_texts()

    def get_parameters_dict(self) -> dict:
        d = dict()
        for i in self._parameters:
            d[i.get_name()] = i
        return d

    def get_images_dict(self) -> dict:
        return {'graph': f'{self.image_folder()}/graph.png'}

    def get_tables_dict(self) -> dict:
        d = dict()
        for i in self._tables:
            d[i.name()] = i
        return d

    def image_folder(self):
        return f'{self.folder()}/images'

    def get_images(self):
        return self._images

    def add_image(self, image: fig):
        self._images.append(image)
        image.savefig(f'{self.image_folder()}/graph.png')

    def write_json(self):
        d = {}
        for i in self._parameters:
            d[i.get_name()] = i.__dict__()
        json_text = json.dumps(d, indent=4)
        f = open(f'{self.parameter_folder()}/param_1.json', 'w', encoding='utf8')
        f.write(json_text)
        f.close()

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
        source_folder = f'sources/{self.lab}'
        self.source = DataSource(source_folder)

        material_folder = f'materials/{self.lab}'
        self.material = DataMaterial(material_folder)

        result_folder = f'results/{self.lab}'
        self.result: DataResult = DataResult(result_folder)
