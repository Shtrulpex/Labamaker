import enum
import pandas as pd
from pandas import DataFrame
import os
import json


class Prefix:
    prefix = {
        'exa': [18, 'Э', 'E'],
        'peta': [15, 'П', 'P'],
        'tera': [12, 'Т', 'T'],
        'giga': [9, 'Г', 'G'],
        'mega': [6, 'М', 'M'],
        'kilo': [3, 'к', 'k'],
        'hecto': [2, 'г', 'h'],
        'deca': [1, 'да', 'da'],
        '': [1, '', ''],
        'deci': [-1, 'д', 'd'],
        'santi': [-2, 'с', 'c'],
        'milli': [-3, 'м', 'm'],
        'micro': [-6, 'мк', 'mk'],
        'nano': [-9, 'н', 'n'],
        'pico': [-12, 'п', 'p'],
        'femto': [-15, 'ф', 'f'],
        'atto': [-18, 'а', 'a']
    }


class Kind:
    def __init__(self, name, prefix: str):
        self.name = name
        if prefix in Prefix.prefix.keys():
            self.prefix = Prefix.prefix[prefix]
        else:
            raise RuntimeError(f'incorrect prefix: {prefix}')
        self.multiplier = 10 ** self.prefix[0]

    def get_multiplier(self):
        return self.multiplier


class MeasUnit:
    def __init__(self, category, kind):
        self.category = category
        self.kind = kind  # Kind object

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


class Kinds(enum.Enum):
    text = 'text'
    formula = 'formula'
    list = 'list'
    title = 'title'


class Text:
    def __init__(self, text_option: dict, kind: str, text: str):
        self.text = text
        self.kind = kind  # text/formula/list/title
        if kind == Kinds.text:
            self.text_option = TextOption(font='arial',
                                          size=12,
                                          bold=False,
                                          color='black',
                                          italics=False,
                                          frame=False,
                                          underline=False)
        elif kind == Kinds.formula:
            self.text_option = TextOption(font='arial',
                                          size=12,
                                          bold=False,
                                          color='black',
                                          italics=False,
                                          frame=True,
                                          underline=False)
        elif kind == Kinds.title:
            self.text_option = TextOption(font='arial',
                                          size=16,
                                          bold=True,
                                          color='black',
                                          italics=False,
                                          frame=False,
                                          underline=True)
        elif kind == Kinds.list:
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
    def __init__(self, value_option: TextOption, unit_option: TextOption, name_option: TextOption):
        self.value_option = value_option
        self.unit_option = unit_option
        self.name_option = name_option

    def get_options(self):
        return {'value': self.value_option,
                'unit': self.unit_option,
                'name': self.name_option}


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


class Parameter:
    def __init__(self, name, value, unit: MeasUnit, options: ParamOptions):
        self.name = name
        self.value = value
        self.unit = unit
        self.options = options

    # Transform from one unit to other (P -> N/m^2) (Па ->  Н/м^2) OR change the prefix
    def convert(self, new_unit: MeasUnit):
        if new_unit.get_category() != self.unit.get_category():
            raise RuntimeError('Incorrect unit to transform')
        multiplier = self.unit.get_multiplier()
        self.value /= multiplier
        self.value *= new_unit.get_multiplier()
        self.unit = new_unit

    def to_si(self):  # transform to SI unit in this category
        category = self.unit.get_category()
        multiplier = self.unit.get_multiplier()
        if category == Category.square:
            self.value /= 10 ** multiplier ** 2
            unit = MeasUnit(Category.length,
                            Kind(Si.square, ''))
            self.unit = unit
        elif category == Category.volume:
            self.value /= 10 ** multiplier ** 3
            unit = MeasUnit(Category.volume,
                            Kind(Si.volume, ''))
            self.unit = unit
        else:
            self.value /= 10 ** multiplier
            unit = MeasUnit(Category[category],
                            Kind(Si[category], ''))
            self.unit = unit


class Table(DataFrame):
    def __init__(self, name, *args):
        self.name = name
        super().__init__(*args)

    def convert(self, column, new_unit: MeasUnit):
        for param in self[column]:
            param.convert(new_unit)


class Data:
    def __init__(self, folder):
        self.folder = folder
        self.tables = self.__form_tables()  # dict of tables: {name: table_obj}
        self.texts = self.__form_texts()  # list of texts (titles, lists, simple texts or formulas)

    def __form_tables(self) -> dict:
        path = self.folder + '\\tables'
        files = os.listdir(path=path)
        tables = dict()
        for file in files:
            name = file.split('\\')[-1].split('.')[0]
            table = Table(name, pd.read_csv(path + '\\' + file, index_col=0))
            tables[name] = table
        return tables

    def __form_texts(self) -> list:
        path = self.folder + '\\texts'
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

    def get_table(self, *name):
        if name:
            return self.tables[name]
        return self.tables

    def get_text(self, *name):
        if name:
            return self.texts[name]
        return self.texts

    def get_description(self):
        return self.folder + '\\description\\description.pdf'


class DataController:
    def __init__(self, folder):
        self.folder = folder
        self.source = None
        self.material = None
        self.result = None
        self.__generate_data()

    def __generate_data(self):
        source_folder = self.folder + '\\source'
        self.source = Data(source_folder)

        material_folder = self.folder + '\\material'
        self.material = Data(material_folder)

        result_folder = self.folder + '\\result'
        self.result = Data(result_folder)

    def get_source(self):
        return self.source

    def get_materials(self):
        return self.material

    def get_result(self):
        return self.result
