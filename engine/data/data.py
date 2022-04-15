import pandas as pd
from pandas import DataFrame, read_csv
import os
import json


class Kind:
    def __init__(self, name, multiplier):
        self.name = name
        self.multiplier = multiplier  # absolute multiplier

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

    def transform(self, new_kind: Kind):
        self.kind = new_kind


class TextOption:
    def __init__(self, font='arial', size=12, bold=False,
                 color='black', italics=False, frame=False):
        self.font = font
        self.size = size
        self.bold = bold
        self.color = color
        self.italics = italics
        self.frame = frame


class Text:
    def __init__(self, text, kind, text_option):
        self.text = text
        self.kind = kind  # text/formula/list
        self.text_option = text_option


class ParamOptions:
    def __init__(self, value_option, unit_option, name_option):
        self.value_option = value_option
        self.unit_option = unit_option
        self.name_option = name_option

    def get_options(self):
        return {'value': self.value_option,
                'unit': self.unit_option,
                'name': self.name_option}


class Parameter:
    def __init__(self, name, value, unit: MeasUnit, options: ParamOptions):
        self.name = name
        self.value = value
        self.unit = unit
        self.options = options

    def transform(self, new_unit: MeasUnit):
        if new_unit.get_category() != self.unit.get_category():
            raise RuntimeError('Incorrect unit to transform')
        self.unit = new_unit

    def to_si(self):  # transform to SI unit in this category
        pass


# form with 2 ways (from table and from pandas)
class Table(DataFrame):
    def __init__(self, name, *args):
        self.name = name
        super().__init__(*args)

    def transform(self, func: Parameter.transform, axis: Axis = 0, *args, **kwargs) -> DataFrame:
        pass


data = [{'a': 1, 'b': 2, 'c':3},
        {'a':10, 'b': 20, 'c': 30}]

t = Table(data, index=['val', 'too'])
t2 = Table(read_csv('123.csv'))
print(t2)
print(type(t2))


class Data:
    def __init__(self, folder):
        self.folder = folder
        self.table = self.form_tables()
        self.text = self.form_texts()

    def get_table(self, *name):
        if name:
            return self.table[name]
        return self.table

    def get_text(self, *name):
        if name:
            return self.text[name]
        return self.text

    def get_description(self):
        return self.folder + '\\description\\description.pdf'

    def form_tables(self) -> dict:
        path = self.folder + '\\tables'
        files = os.listdir(path=path)
        tables = dict()
        for file in files:
            name = file.split('\\')[-1].split('.')[0]
            table = Table(name, pd.read_csv(file))
            tables[name] = table
        return tables

    def form_texts(self) -> dict:
        desc_path = self.folder + '\\text\\description.pdf'


