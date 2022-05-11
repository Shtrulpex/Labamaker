import enum
import pandas as pd
import os
import shutil
import json


class Prefix:
    @staticmethod
    def load_prefix():
        with open('units.json', 'r', encoding='utf8') as f:
            data = json.load(f)
            return data['prefix']

    __prefixes = load_prefix()

    def __init__(self, prefix: str):
        if prefix in Prefix.__prefixes:
            self.prefix = Prefix.__prefixes[prefix]
            self.multiplier = self.prefix[0]
        else:
            raise RuntimeError(f'incorrect prefix: {prefix}')

    def get_prefix(self, language='en'):
        if language == 'en':
            return self.prefix[2]
        elif language == 'ru':
            return self.prefix[1]
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


class TextOption:
    def __init__(self, font: str = 'arial',
                 size: int = 12,
                 bold: bool = False,
                 color: str = 'black',
                 italics: bool = False,
                 frame: bool = False,
                 underline: bool = False):
        self.font = font
        self.size = size
        self.bold = bold
        self.color = color
        self.italics = italics
        self.frame = frame
        self.underline = underline


class Text:
    class Kinds(enum.Enum):
        text = 'text'
        formula = 'formula'
        list = 'list'
        title = 'title'
        
    def __init__(self, text_option: dict, kind: str, text: str):
        self.text = text
        self.kind = kind  # text/formula/list/title
        if kind == Text.Kinds.text:
            self.text_option = TextOption(font='arial',
                                          size=12,
                                          bold=False,
                                          color='black',
                                          italics=False,
                                          frame=False,
                                          underline=False)
        elif kind == Text.Kinds.formula:
            self.text_option = TextOption(font='arial',
                                          size=12,
                                          bold=False,
                                          color='black',
                                          italics=False,
                                          frame=True,
                                          underline=False)
        elif kind == Text.Kinds.title:
            self.text_option = TextOption(font='arial',
                                          size=16,
                                          bold=True,
                                          color='black',
                                          italics=False,
                                          frame=False,
                                          underline=True)
        elif kind == Text.Kinds.list:
            self.text_option = TextOption(font='arial',
                                          size=12,
                                          bold=False,
                                          color='black',
                                          italics=True,
                                          frame=False,
                                          underline=True)
        else:
            font = text_option['font'],
            size = text_option['size'],
            bold = text_option['bold'],
            color = text_option['color'],
            italics = text_option['italics'],
            frame = text_option['frame'],
            underline = text_option['underline']
            self.text_option = TextOption(font=font,
                                          size=size,
                                          bold=bold,
                                          color=color,
                                          italics=italics,
                                          frame=frame,
                                          underline=underline)


class ParamOptions:
    def __init__(self, value_option: TextOption,
                 unit_option: TextOption,
                 name_option: TextOption):
        self.__value_option = value_option
        self.__unit_option = unit_option
        self.__name_option = name_option

    def get_options(self):
        return {'value': self.__value_option,
                'unit': self.__unit_option,
                'name': self.__name_option}


class Parameter:
    class Category(enum.Enum):
        number = 'number'
        length = 'length'
        square = 'square'
        volume = 'volume'
        mass = 'mass'
        time = 'time'
        temperature = 'temperature'
        amperage = 'amperage'
        resistance = 'resistance'

    class Si(enum.Enum):
        number = 'unit'
        length = 'm'
        square = 'm^2'
        volume = 'm^3'
        mass = 'kg'
        time = 's'
        temperature = 'K'
        amperage = 'A'
        resistance = 'Om'
        
    def __init__(self, name: str, value: float, unit: MeasUnit, options: ParamOptions):
        self.name = name
        self.value = value
        self.unit = unit
        self.options = options

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
        if category == Parameter.Category.square:
            self.value /= multiplier ** 2
        elif category == Parameter.Category.volume:
            self.value /= multiplier ** 3
        else:
            self.value /= multiplier
        unit = MeasUnit(category, Kind(Parameter.Si[category], ''))
        self.unit = unit


class Table(pd.DataFrame):
    def __init__(self, name: str, *args):
        self.name = name
        super().__init__(*args)

    def convert(self, column: str, new_unit: MeasUnit):
        if column not in self.columns:
            raise RuntimeError(f'Wrong column name: {column}')
        for param in self[column]:
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
            for txt in texts_.keys():
                text = Text(texts_[txt]['options'],
                            texts_[txt]['kind'],
                            texts_[txt]['text'])
                self._texts.append(text)
        shutil.move(filepath, path)


class DataSource(Data):
    def __init__(self, folder: str):
        super(DataSource, self).__init__(folder)
        self._tables = self.__form_tables()  # dict of tables: {name: table_obj}
        self._texts = self.__form_texts()  # list of texts (titles, lists, simple texts or formulas)

    def __form_tables(self) -> dict:
        path = self._folder + '\\tables'
        files = os.listdir(path=path)
        tables = dict()
        for file in files:
            name = file.split('\\')[-1].split('.')[0]
            table = Table(name, pd.read_csv(path + '\\' + file, index_col=0))
            tables[name] = table
        return tables

    def __form_texts(self) -> list:
        path = self._folder + '\\texts'
        files = os.listdir(path=path)
        texts = []
        for file in files:
            with open(path + '\\' + file, 'r', encoding='utf8') as f:
                data = json.load(f)
                texts_ = data['texts']
                for txt in texts_.keys():
                    text = Text(texts_[txt]['options'],
                                texts_[txt]['kind'],
                                texts_[txt]['text'])
                    texts.append(text)
        return texts

    # КАК УДАЛИТЬ МЕТОД?!?!?!
    # @property
    # def add_table(self, filepath):
    #     raise AttributeError("'DataSource' object has no attribute 'add_table'")

    def get_description(self):
        return self._folder + '\\description.pdf'


class DataResult(Data):
    def __init__(self, folder: str):
        super(DataResult, self).__init__(folder)
        self._images = []

    def add_image(self, filepath: str):
        path = self._folder + '\\images'
        name = filepath.split('\\')[-1]  # !!! name with file extension (for example: .png)
        if name in self._images:
            raise RuntimeError(f'Image "{name}" also exists!: locates in {path}')
        self._images.append(name)
        shutil.move(filepath, path)

    def get_images(self):
        return self._images


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
