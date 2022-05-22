import enum
import pandas as pd
import os
import shutil
import json


class Prefix:
    with open('units.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        __prefixes = data['prefix']

    def __init__(self, prefix: str):
        if prefix in Prefix.__prefixes:
            self.__prefix = Prefix.__prefixes[prefix]
            self.multiplier = self.__prefix[0]
        else:
            raise RuntimeError(f'incorrect prefix: {prefix}')

    def get_prefix(self, language='en'):
        if language == 'en':
            return self.__prefix[2]
        elif language == 'ru':
            return self.__prefix[1]
        raise RuntimeError(f"incorrect language: {language}\n"
                           f"(accessible: 'en' or 'ru', not {language})")
        

class Kind:
    def __init__(self, name: str, prefix: str):
        self.name = name
        self.prefix = Prefix(prefix)
        self.multiplier = 10 ** self.prefix.multiplier

    def get_multiplier(self):
        return self.multiplier


class MeasUnit:
    def __init__(self, category: str, kind: Kind):
        self.category = category
        self.kind = kind

    def get_category(self):
        return self.category

    def get_multiplier(self):
        return self.kind.get_multiplier()


class TextKinds(enum.Enum):
    text = 'text'
    formula = 'formula'
    list = 'list'
    title = 'title'
    default = 'default'


class TextOption:
    with open('text_options.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        __options = data['options']
        __kinds_options = data['kinds_options']

    @classmethod
    def __fill_options(cls, **kwargs):
        kind = TextOption.__kinds_options[kwargs['kind']]
        for option in TextOption.__options:
            if option not in kwargs.keys():
                kwargs[option] = kind[option]
        return kwargs

    def __init__(self, kind: str = TextKinds.default.name, **kwargs):
        kwargs = TextOption.__fill_options(kind=kind, **kwargs)
        self.font = kwargs['font']
        self.size = kwargs['size']
        self.bold = kwargs['bold']
        self.color = kwargs['color']
        self.italics = kwargs['italics']
        self.frame = kwargs['frame']
        self.underline = kwargs['underline']


class Text:
    def __init__(self, text: str = '',
                 kind: str = TextKinds.default.value,
                 **params):
        self.text = text
        self.kind = kind  # text/formula/list/title
        self.options = TextOption(kind=kind, **params)


class ParamOptions:
    def __init__(self, value_option: TextOption,
                 unit_option: TextOption,
                 name_option: TextOption):
        self.value_option = value_option
        self.unit_option = unit_option
        self.name_option = name_option


class Parameter:
    with open('units.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        symbol = dict()
        for key in data['unit'].keys():
            symbol[key] = data['unit'][key][0]
    __Symbol = enum.Enum(
        value='__Symbol',
        names=symbol
    )

    with open('units.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        category = dict()
        for key in data['unit'].keys():
            category[key] = key
    __Category = enum.Enum(
        value='__Category',
        names=category
    )

    with open('units.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        si = dict()
        for key in data['unit'].keys():
            si[key] = data['unit'][key][1]
    __Si = enum.Enum(
        value='__Si',
        names=si
    )
        
    def __init__(self, name: str,
                 value: float,
                 unit: MeasUnit,
                 options: ParamOptions):
        self.name = name
        self.value = value
        self.unit = unit
        self.options = options
        self.symbol = Parameter.__Symbol[unit.get_category()]

    # Transform from one unit to other (P -> N/m^2) (Па ->  Н/м^2) OR change the prefix
    def convert(self, new_unit: MeasUnit):
        if new_unit.get_category() != self.unit.get_category():
            raise RuntimeError(f'Incorrect unit to transform (wrong category):\t'
                               f'{new_unit.get_category()} to {self.unit.get_category()}')
        multiplier = self.unit.get_multiplier()
        self.value /= multiplier
        self.value *= new_unit.get_multiplier()
        self.unit = new_unit

    def to_si(self):  # transform to SI unit in this category
        category = self.unit.get_category()
        multiplier = self.unit.get_multiplier()
        if category == Parameter.__Category.square:
            self.value /= multiplier ** 2
        elif category == Parameter.__Category.volume:
            self.value /= multiplier ** 3
        else:
            self.value /= multiplier
        unit = MeasUnit(category, Kind(Parameter.__Si[category], ''))
        self.unit = unit


class Table:
    def __init__(self, name: str, file: str):
        self.name = name
        self.table = pd.read_csv(file, index_col=0)

    def convert(self, column: str, new_unit: MeasUnit):
        if column not in self.table.columns:
            raise RuntimeError(f'Wrong column name: {column}')
        for param in self.table[column]:
            param.convert(new_unit)


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
        table = Table(name, pd.read_csv(filepath, index_col=0))
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
        self._texts = self.__form_parameters()  # list of texts (titles, lists, simple texts or formulas)

    def __form_tables(self):
        path = self._folder + '\\tables'
        files = os.listdir(path=path)
        for file in files:
            if file.endswith('.csv'):
                name = file.split('\\')[-1].split('.')[0]
                table = Table(name, path + '\\' + file)
                self._tables[name] = table

    def __form_parameters(self) -> list:
        pass

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
