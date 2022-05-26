import os
import shutil

from parameter import *
from table import *


class Data:
    def __init__(self, folder: str):
        self._folder = folder
        self._tables = dict()  # dict of tables: {name: table_obj}
        self._texts = []  # list of texts (titles, lists, simple texts or formulas)

    def get_tables(self, *name):
        if name:
            return self._tables[name]
        return self._tables

    def get_texts(self):
        return self._texts

    def add_table(self, filepath: str):
        path = self._folder + '\\tables'
        name = filepath.split('\\')[-1].split('.')[0]
        if name in self._tables.keys():
            raise RuntimeError(f'Table "{name}" also exists!: locates in {path}')
        table = Table(name + '.csv', filepath)
        self._tables[name] = table
        shutil.move(filepath, path)

    def add_text(self, filepath: str):
        path = self._folder + '\\texts'
        with open(filepath, 'r', encoding='utf8') as f:
            data = json.load(f)
            texts_ = data['texts']
            for text in texts_:
                self._texts.append(Text(text=text['text'],
                                        kind=text['kind'],
                                        **text['options']))
        shutil.move(filepath, path)


class DataSource(Data):
    def __init__(self, folder: str):
        super(DataSource, self).__init__(folder)
        self.__form_tables()  # self._tables = dict of tables: {name: table_obj}
        self.__form_parameters()  # list of texts (titles, lists, simple texts or formulas)

    def __form_tables(self):
        path = self._folder + '\\tables'
        files = os.listdir(path=path)
        for file in files:
            table = Table(file.split('\\')[-1], path + '\\' + file)
            if table.name not in self._tables.keys():
                self._tables[table.name] = table

    def __form_parameters(self):
        path = self._folder + '\\texts'
        files = os.listdir(path=path)
        for file in files:
            if file.startswith('param'):
                with open(path + '\\' + file, 'r', encoding='utf8') as f:
                    data = json.load(f)
                    self.__set_file_parameters(data)

    def __set_file_parameters(self, data: dict):
        for parameter in data.keys():
            options = ParamOptions(**data[parameter]['options'])
            category = data[parameter]['category']
            prefix, name = DataSource._parser.parse(
                data[parameter]['unit']
            )
            meas_unit = MeasUnit(
                category,
                Kind(name, prefix)
            )
            value = data[parameter]['value']
            absolute_error = None
            if 'absolute_error' in data[parameter].keys():
                absolute_error = data[parameter]['absolute_error']
            param = Parameter(
                parameter,
                value,
                meas_unit,
                options,
                absolute_error
            )
            self._texts.append(param)

    def get_description(self):
        return self._folder + '\\description.pdf'


class DataResult(Data):
    def __init__(self, folder: str):
        super().__init__(folder)
        self._images = []
        self._texts = self.__form_texts()

    def add_image(self, filepath: str):
        path = self._folder + '\\images'
        name = filepath.split('\\')[-1]  # !!! name with file extension (for example: .png)
        if name in self._images:
            raise RuntimeError(f'Image "{name}" also exists!: locates in {path}')
        self._images.append(name)
        shutil.move(filepath, path)

    def get_images(self):
        return self._images

    def __form_texts(self) -> list:
        path = self._folder + '\\texts'
        files = os.listdir(path=path)
        texts = []
        for file in files:
            with open(path + '\\' + file, 'r', encoding='utf8') as f:
                data = json.load(f)
                texts_ = data['texts']
                for text in texts_:
                    texts.append(Text(text=text['text'],
                                      kind=text['kind'],
                                      **text['options']))
        return texts


class DataMaterial(Data):
    pass


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
dc.material.add_table('C:\\Users\\v3531\\Downloads\\measures_1.csv')
print('All is good')
