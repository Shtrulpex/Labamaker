import enum
import pandas as pd
import os
import shutil
import json


# the entity specifying the multiplier and the simple prefix string
class Prefix:
    # load list of prefixes dictionaries from file. Example:
    # "micro": [-6, "мк", "mk"] etc.
    with open('units.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        __prefixes = data['prefix']  # key - full name of prefix
        __en_prefixes = dict()  # key - short EN name of prefix
        __ru_prefixes = dict()  # key - short RU name of prefix
        for current_prefix in data['prefix'].keys():
            __en_prefixes[data['prefix'][current_prefix][2]] = current_prefix
            __ru_prefixes[data['prefix'][current_prefix][1]] = current_prefix

    def __init__(self, prefix: str):
        # for example:
        # Prefix('mk') or Prefix ('micro')
        if prefix in Prefix.__en_prefixes.keys():
            full_name_of_prefix = Prefix.__en_prefixes[prefix]
        elif prefix in Prefix.__ru_prefixes.keys():
            full_name_of_prefix = Prefix.__ru_prefixes[prefix]
        elif prefix in Prefix.__prefixes.keys():
            full_name_of_prefix = prefix
        else:
            raise RuntimeError(f'incorrect prefix: {prefix}')
        self.__prefix = Prefix.__prefixes[full_name_of_prefix]
        self.__multiplier = Prefix.__prefixes[full_name_of_prefix][0]

    def get_prefix_string(self, language='en'):
        if language == 'en':
            return self.__prefix[2]
        elif language == 'ru':
            return self.__prefix[1]
        raise RuntimeError(f"incorrect language: {language}\n"
                           f"(accessible: 'en' or 'ru', not {language})")

    def get_multiplier(self):
        return self.__multiplier


class Kind:
    with open('units.json', 'r', encoding='utf8') as f:
        _derived_units = json.load(f)['derived_units']

    with open('units.json', 'r', encoding='utf8') as f:
        _base_units = json.load(f)['base_units']

    def __init__(self):
        self.__multiplier = None

    def get_multiplier(self):
        return self.__multiplier

    def get_unit_string(self):
        pass


# the kind of derived_unit
# with particular prefixes
# Examples:
#   (m) || (mm) || (s)
# P.S. you can see list of base_units in "units.json\base_units"
class BaseKind(Kind):
    def __init__(self, prefix: str, base_unit: str):
        super().__init__()
        self.__prefix = Prefix(prefix)
        self.__unit = BaseKind._base_units[base_unit][1]
        self.__multiplier = self.__prefix.get_multiplier()

    def get_unit_string(self):
        return f'{self.__prefix.get_prefix_string()}' \
               f'{self.__unit}'

    def set_prefix(self, prefix: str):
        pass

    def to_si(self):
        pass


# the kind of derived_unit
# with particular prefixes
# Examples:
#   (m)/(s^2) || (mm)/(s^2),
#   (J) || (kg*m^2)/(s^2) <- physical work
class DerivedKind(Kind):
    class Fraction(enum.Enum):
        numerator = 'numerator'
        denominator = 'denominator'
        base = 'base'
        derived = 'derived'

    s1 = Fraction.numerator.value
    s2 = Fraction.denominator.value

    @classmethod
    def init_from_file(cls, data: dict):
        numerator = DerivedKind.s1
        denominator = DerivedKind.s2
        base = DerivedKind.Fraction.base.value
        derived = DerivedKind.Fraction.derived.value

        numer = []
        denomin = []

        if DerivedKind.s1 not in data.keys():
            raise RuntimeError(f"can't find keys: {DerivedKind.s1}")
        if DerivedKind.s2 not in data.keys():
            raise RuntimeError(f"can't find keys: {DerivedKind.s2}")
        for base_kind in data[numerator][base]:
            numer.append(BaseKind(
                base_kind[0],
                base_kind[1]
            ))
        for derived in data[numerator][derived]:
            numer.append(cls.__init_single(**derived))
        for base_kind in data[denominator][base]:
            denomin.append(BaseKind(
                base_kind[0],
                base_kind[1]
            ))
        for derived in data[denominator][derived]:
            denominator.append(cls.__init_single(**derived))
        d = {'numerator': numer,
             'denominator': denomin}
        return cls(**d)

    # init_single_derived_unit_from_file
    @classmethod
    def __init_single(cls, **data):
        numerator = DerivedKind.s1
        denominator = DerivedKind.s2

        numer = []
        denomin = []

        for base_kind in data[numerator]:
            numer.append(BaseKind(
                base_kind[0],
                base_kind[1]
            ))
        for base_kind in data[denominator]:
            denomin.append(BaseKind(
                base_kind[0],
                base_kind[1]
            ))
        d = {'numerator': numer,
             'denominator': denomin}
        return cls(**d)

    def __init__(self, **units: Kind):
        super().__init__()
        numerator = DerivedKind.s1
        denominator = DerivedKind.s2
        self.__numerator = units[numerator]  # list if Kinds
        self.__denominator = units[denominator]  # list if Kinds
        self.__multiplier = self.__generate_multiplier()

    def __generate_multiplier(self):
        multiplier = 1
        for kind in self.__numerator:
            multiplier *= kind.get_multiplier()
        for kind in self.__denominator:
            multiplier *= kind.get_multiplier()
        return multiplier

    def get_unit_string(self):
        s1 = '*'.join(i.get_unit_string for i in self.__numerator)
        s2 = '*'.join(i.get_unit_string for i in self.__denominator)
        return f'({s1})/({s2})'

    def set_prefix(self):
        pass

    def to_si(self):
        pass


class MeasUnit:
    def __init__(self, category: str, kind: Kind):
        self.__category = category
        self.__kind = kind

    def __str__(self):
        return self.get_unit_string()

    def __repr__(self):
        return str(self)

    def get_category(self):
        return self.__category

    def get_multiplier(self):
        return self.__kind.get_multiplier()

    def get_unit_string(self):
        return self.__kind.get_unit_string()


# class Parser:
#     __Base_units = []
#     with open('units.json', 'r', encoding='utf8') as f:
#         data = json.load(f)
#         for unit in data['unit'].keys():
#             __Base_units.append(data['unit'][unit][1])
#
#     @staticmethod
#     def __reverse_all(strings):
#         for i in range(len(strings)):
#             strings[i] = strings[i][::-1]
#         return strings
#
#     @staticmethod
#     def __end_replace(s: str, s1: str, s2: str):
#         a = [s, s1, s2]
#         a = Parser.__reverse_all(a)
#         s = s.replace(a[1], a[2], 1)
#         s = s[::-1]
#         return s
#
#     # now it is a simplistic parser!!! from unit to (prefix, base_unit)
#     @staticmethod
#     def parse(unit: str):
#         for base_unit in Parser.__Base_units:
#             if unit.endswith(base_unit):
#                 if unit == base_unit:
#                     return '', base_unit
#                 prefix = Parser.__end_replace(unit, base_unit, '')
#                 return prefix, base_unit


class TextKinds(enum.Enum):
    text = 'text'
    formula = 'formula'
    list = 'list'
    title = 'title'
    default = 'default'

    par_val = 'parameter_value'
    par_abs_err = 'parameter_absolute_error'
    par_rel_err = 'parameter_relative_error'
    par_unit = 'parameter_unit'
    par_name = 'parameter_name'
    par_symb = 'parameter_symbol'


class Option:
    with open('text_options.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        _options = data['options']
        _kinds_options = data['kinds_options']

    @classmethod
    def _fill_options(cls, **kwargs):
        kind = Option._kinds_options[kwargs['kind']]
        for option in Option._options:
            if option not in kwargs.keys():
                kwargs[option] = kind[option]
        return kwargs


class TextOption(Option):
    def __init__(self, kind: str = TextKinds.default.name, **kwargs):
        kwargs = TextOption._fill_options(kind=kind, **kwargs)
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


class ParamOptions(Option):
    def __init__(self, **kwargs):
        for option in kwargs.keys():
            kwargs[option] = ParamOptions._fill_options(
                kind='parameter_' + option,
                **kwargs[option]
            )
        self.value_option = kwargs['value']
        if 'absolute_error' in kwargs.keys():
            self.absolute_error_option = kwargs['absolute_error']
            self.relative_error_option = kwargs['relative_error']
        self.unit_option = kwargs['unit']
        self.name_option = kwargs['name']
        self.symbol_option = kwargs['symbol']


class Parameter:
    __Counter = {}
    __Symbol = dict()
    __Category = dict()
    __Si = dict()

    with open('units.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        symbol = dict()
        for key in data['unit'].keys():
            __Symbol[key] = data['unit'][key][0]

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
                 options: ParamOptions,
                 *absolute_error
                 ):
        self.name = name
        self.value = value
        if absolute_error[0]:
            self.abs_error = absolute_error[0]
            self.rel_err = self.abs_error / value * 100
        else:
            self.abs_error = None
            self.rel_err = None
        self.unit = unit

        self.options = options

        symbol = str(Parameter.__Symbol[unit.get_category()])
        if symbol in Parameter.__Counter.keys():
            Parameter.__Counter[symbol] += 1
        else:
            Parameter.__Counter[symbol] = 1
        self.symbol = symbol + '_' + str(Parameter.__Counter[symbol])

    # Transform from one unit to other (P -> N/m^2) (Па ->  Н/м^2) OR change the prefix
    def convert(self, new_unit: MeasUnit):
        if new_unit.get_category() != self.unit.get_category():
            raise RuntimeError(f'Incorrect unit to transform (wrong category):\t'
                               f'{new_unit.get_category()} to {self.unit.get_category()}')
        self.__recount_value(new_unit)
        self.__recount_absolute_error(new_unit)
        self.unit = new_unit

    def __recount_value(self, new_unit: MeasUnit):
        multiplier = self.unit.get_multiplier()
        self.value /= multiplier
        self.value *= new_unit.get_multiplier()

    def __recount_absolute_error(self, new_unit: MeasUnit):
        multiplier = self.unit.get_multiplier()
        self.abs_error /= multiplier
        self.abs_error *= new_unit.get_multiplier()

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

    def get_unit(self):
        return str(self.unit)

    def __str__(self):
        if self.abs_error:
            s = f'{self.symbol} = {self.value} ± {str(self.abs_error)} {str(self.unit)}'
        else:
            s = f'{self.symbol} = {self.value} {str(self.unit)}'
        return s

    def __repr__(self):
        return str(self)


class Table:
    def __init__(self, name: str, file: str):
        self.name = name.split('.')[0]
        if name.endswith('.csv'):
            self.table = pd.read_csv(file, index_col=0)

    def convert(self, column: str, new_unit: MeasUnit):
        if column not in self.table.columns:
            raise RuntimeError(f'Wrong column name: {column}')
        for param in self.table[column]:
            param.convert(new_unit)


class Data:
    _parser = Parser()

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
