from __future__ import annotations
import json
import enum


# the entity specifying the multiplier and the simple prefix string
class Prefix:
    def __init__(self, prefix: str | int):
        # for example:
        # Prefix('mk') or Prefix ('micro')
        if prefix is int:
            self.__prefix = [prefix, f'10^{prefix} ', f'10^{prefix} ']
            self.__multiplier = prefix
        else:
            if prefix in Prefix.__multipliers.keys():
                full_name_of_prefix = Prefix.__multipliers[prefix]
            elif prefix in Prefix.__en_prefixes.keys():
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

    # load list of prefixes dictionaries from file. Example:
    # "micro": [-6, "мк", "mk"] etc.
    with open('units.json', 'r', encoding='utf8') as f:
        data = json.load(f)
        __prefixes = data['prefix']  # key - full name of prefix
        __en_prefixes = dict()  # key - short EN name of prefix
        __ru_prefixes = dict()  # key - short RU name of prefix
        __multipliers = dict()  # key - the degree of prefix
        for current_prefix in data['prefix'].keys():
            __en_prefixes[data['prefix'][current_prefix][2]] = current_prefix
            __ru_prefixes[data['prefix'][current_prefix][1]] = current_prefix
            __multipliers[data['prefix'][current_prefix][0]] = current_prefix

    def __mul__(self, other: Prefix):
        return Prefix(self.get_multiplier() + other.get_multiplier())

    def __truediv__(self, other: Prefix):
        return Prefix(self.get_multiplier() + other.get_multiplier())


class MeasUnit:
    @staticmethod
    def init_from_file(data):
        if data[0] == 'base':
            base_unit = BaseMeasUnit.init_from_tokens(*data[1:])
            d = {
                'numerator': [base_unit],
                'denominator': []
            }
            return DerivedMeasUnit(
                base_unit.get_symbol(),
                base_unit.get_category(),
                **d
            )
        elif data[0] == 'derived':
            return DerivedMeasUnit.init_from_tokens(*data[1:])

    def __init__(self, category: str):
        self.__multiplier = None
        self.__symbol = None
        self.__category = category

    def get_multiplier(self):
        return self.__multiplier

    def get_symbol(self):
        return self.__symbol

    def get_category(self):
        return self.__category
    
    def to_si(self):
        pass

    with open('units.json', 'r', encoding='utf8') as f:
        _derived_units = json.load(f)['derived_units']

    with open('units.json', 'r', encoding='utf8') as f:
        _base_units = json.load(f)['base_units']

    with open('units.json', 'r', encoding='utf8') as f:
        _constants = json.load(f)['constants']

    def __multiply(self, other: MeasUnit):
        pass

    def __divide(self, other: MeasUnit):
        pass
    
    def __get_flipped(self):
        pass
    
    def __pow(self, power: float):
        pass

    def __get_unit_string(self):
        pass

    def __str__(self):
        return self.__get_unit_string()

    def __repr__(self):
        return str(self)

    def __mul__(self, other: MeasUnit):
        return self.__multiply(other)
    
    def __pow__(self, power: float):
        return self.__pow(power)

    def __truediv__(self, other: MeasUnit):
        return self.__divide(other)

    def __eq__(self, other: MeasUnit):
        return str(self) == str(other)

    def __ne__(self, other: MeasUnit):
        return not self == other


# the unit of derived_unit with particular prefixes and degree
# Examples:
#   (m) || (mm) || (s) || (sm)^2
# P.S. you can see list of base_units in "units.json\base_units"
class BaseMeasUnit(MeasUnit):
    @classmethod
    def init_from_tokens(
            cls,
            category: str,
            prefix: str,
            degree: float):
        return cls(prefix, category, degree)

    @classmethod
    def init_from_other_base(cls, unit: BaseMeasUnit):
        prefix = unit.get_prefix()
        category = unit.get_category()
        degree = unit.get_degree()
        return BaseMeasUnit(prefix, category, degree)

    def __init__(self,
                 prefix: str,
                 category: str,
                 degree: float = 1.0):
        super().__init__(category)
        data = BaseMeasUnit._base_units[category]
        self.__symbol = data[0]
        self.__unit = data[1]
        self.__degree = degree * data[2]
        
        self.__prefix = Prefix('')
        self.__multiplier = 1
        self.set_prefix(prefix)
    
    def get_degree(self):
        return self.__degree
    
    def get_prefix(self):
        return self.__prefix

    def set_prefix(self, prefix: str):
        self.__prefix = Prefix(prefix)
        self.__update_multiplier()

    def set_degree(self, n: float):
        self.__degree = n
        self.__update_multiplier()

    def to_si(self):
        self.set_prefix("")

    def __get_unit_string(self):
        s = f'{self.__prefix.get_prefix_string()}{self.__unit}'
        if self.get_degree() == 1:
            return s
        return f'{s}^[{self.get_degree()}]'

    def __update_multiplier(self):
        self.__multiplier = 10 ** (self.__prefix.get_multiplier() * self.__degree)

    def __multiply(self, other: BaseMeasUnit) -> BaseMeasUnit:
        if self != other:
            raise RuntimeError(f'incorrect categories of multipliers')
        degree = self.get_degree() + other.get_degree()
        if degree == 0:
            category = 'number'
        else:
            category = self.get_category()
        prefix = self.__prefix * other.__prefix
        return BaseMeasUnit(prefix, category, degree)

    def __get_flipped(self):
        unit = BaseMeasUnit.init_from_other_base(self)
        unit.set_degree(-unit.get_degree())
        return unit

    def __divide(self, other: BaseMeasUnit):
        other = other.__get_flipped()
        return self.__multiply(other)
    
    def __pow(self, power: float):
        prefix = self.get_prefix()
        category = self.get_category()  #!&&!&!&!&!&!&^!@#%%@!$&TGU!FYDFUI !I
        degree = self.get_degree() * power
        unit = BaseMeasUnit(prefix, category, degree)
        return unit


# the unit of derived_unit with particular prefixes
# Examples:
#   (m)/(s^2) || (mm)/(s^2),
#   (J) || (kg*m^2)/(s^2) <- physical work бирююююк
class DerivedMeasUnit(MeasUnit):
    @classmethod
    def init_from_tokens(
            cls,
            category: str,
            index: int,
            prefixes: list):
        numerator = DerivedMeasUnit.Fraction.numerator.value
        denominator = DerivedMeasUnit.Fraction.denominator.value
        unit = DerivedMeasUnit._derived_units[category]
        symbol = unit[0]
        template = unit[1][index]
        if numerator not in template.keys():
            raise RuntimeError(f"can't find key: {numerator}")
        if denominator not in template.keys():
            raise RuntimeError(f"can't find key: {denominator}")

        def __generate_base_units(prefixes_, units):
            a = []
            for i in range(len(units)):
                category_ = units[i][0]
                degree_ = units[i][1]
                a.append(BaseMeasUnit(
                    prefixes_[i],
                    category_,
                    degree_))
            return a

        sp1 = template[numerator]
        sp2 = template[denominator]
        l1 = len(sp1)
        numer = __generate_base_units(prefixes[:l1], sp1)
        denom = __generate_base_units(prefixes[l1:], sp2)
        d = {
            numerator: numer,
            denominator: denom
        }
        return cls(symbol, category, **d)
    
    @classmethod
    def init_from_other_derived(cls, unit: DerivedMeasUnit):
        symbol = unit.get_symbol()
        category = unit.get_category()
        units = unit.get_units()
        return cls(symbol, category, **units)

    def __init__(self, symbol: str, category: str, **units):
        super().__init__(category)
        numerator = DerivedMeasUnit.Fraction.numerator.value
        denominator = DerivedMeasUnit.Fraction.denominator.value
        self.__numerator = units[numerator]  # list if Kinds
        self.__denominator = units[denominator]  # list if Kinds
        self.__symbol = symbol
        self.__multiplier = 1
        self.__update_multiplier()

    def get_units(self):
        numerator = DerivedMeasUnit.Fraction.numerator.value
        denominator = DerivedMeasUnit.Fraction.denominator.value
        d = {
            numerator: self.get_numerator(),
            denominator: self.get_denominator()
        }
        return d

    def get_numerator(self):
        return self.__numerator

    def get_denominator(self):
        return self.__denominator

    def set_prefix(self, unit: BaseMeasUnit, prefix: str):
        if unit in self.get_numerator():
            i = self.get_numerator().index(unit)
            self.__numerator[i].set_prefix(prefix)
        elif unit in self.get_denominator():
            i = self.get_denominator().index(unit)
            self.__denominator[i].set_prefix(prefix)
        else:
            raise RuntimeError(f"""No such unit ({str(unit)}) in {str(self)}""")

    def to_si(self):
        for unit in self.get_numerator():
            unit.to_si()
        for unit in self.__denominator:
            unit.to_si()
        self.__update_multiplier()

    def __get_unit_string(self):
        s1 = '*'.join(str(i) for i in self.get_numerator())
        s2 = '*'.join(str(i) for i in self.get_denominator())
        return f'({s1})/({s2})'

    def __multiply(self, other: DerivedMeasUnit):
        new_unit = DerivedMeasUnit.init_from_other_derived(self)
        numerator = DerivedMeasUnit.Fraction.numerator.value
        other_numer = other.get_numerator()
        other_denom = other.get_denominator()
        for i in range(len(other_numer)):
            find = new_unit.__find_unit_in_fraction(other_numer[i])
            if find:
                part = find[0]
                index = find[1]
                if part == numerator:
                    new_unit.__numerator[index] =\
                        new_unit.get_numerator()[index] * other_numer[i]
                else:
                    new_unit.__denominator[index] = \
                        new_unit.get_denominator()[index] * other_numer[i]
            else:
                new_unit.__numerator.append(other_numer[i])
        for i in range(len(other_denom)):
            find = new_unit.__find_unit_in_fraction(other_denom[i])
            if find:
                part = find[0]
                index = find[1]
                if part == numerator:
                    new_unit.__numerator[index] =\
                        new_unit.get_numerator()[index] * other_denom[i]
                else:
                    new_unit.__denominator[index] = \
                        new_unit.get_denominator()[index] * other_denom[i]
            else:
                new_unit.__numerator.append(other_denom[i])
        new_unit.__update_multiplier()
        return new_unit

    def __get_flipped(self):
        unit = DerivedMeasUnit.init_from_other_derived(self)
        unit.__denominator, unit__numerator\
            = unit.get_numerator(), unit.get_denominator()
        return unit

    def __divide(self, other: DerivedMeasUnit):
        other = other.__get_flipped()
        return self.__multiply(other)
        
    def __pow(self, power: float):
        numer = self.get_numerator()
        denom = self.get_denominator()
        for i in range(len(numer)):
            numer[i] = numer[i] ** power
        for i in range(len(denom)):
            denom[i] = denom[i] ** power
        symbol = self.get_symbol()
        category = self.get_category()  # ewofugwe;ifbweifgweoahdq&!&!&!&!
        numerator = DerivedMeasUnit.Fraction.numerator.value
        denominator = DerivedMeasUnit.Fraction.denominator.value
        units = {
            numerator: numer,
            denominator: denom
        }
        return DerivedMeasUnit(symbol, category, **units)

    def __find_unit_in_fraction(self, unit: BaseMeasUnit):
        numerator = DerivedMeasUnit.Fraction.numerator.value
        denominator = DerivedMeasUnit.Fraction.denominator.value
        numer = self.get_numerator()
        denom = self.get_denominator()
        for i in range(len(numer)):
            if numer[i].get_category() == unit.get_category():
                return numerator, i
        for i in range(len(denom)):
            if denom[i].get_category() == unit.get_category():
                return denominator, i
        return False

    def __update_multiplier(self):
        multiplier = 1
        for unit in self.get_numerator():
            multiplier *= unit.get_multiplier()
        for unit in self.get_denominator():
            multiplier /= unit.get_multiplier()
        self.__multiplier = multiplier

    class Fraction(enum.Enum):
        numerator = 'numerator'
        denominator = 'denominator'
        base = 'base'
        derived = 'derived'
