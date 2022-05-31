from __future__ import annotations
import json
import enum
import os


# the entity specifying the multiplier and the simple prefix string
class Prefix:
    def __init__(self, prefix: str | int | Prefix):
        # for example:
        # Prefix('mk') or Prefix ('micro')
        if type(prefix) == Prefix:
            self.__prefix = prefix.__prefix
            self.__multiplier = prefix.__multiplier
        elif type(prefix) in (int, float):
            if prefix in Prefix.__multipliers.keys():
                full_name_of_prefix = Prefix.__multipliers[prefix]
                self.__prefix = Prefix.__prefixes[full_name_of_prefix]
                self.__multiplier = Prefix.__prefixes[full_name_of_prefix][0]
            else:
                self.__prefix = [prefix, f'10^{prefix} ', f'10^{prefix} ']
                self.__multiplier = prefix
        else:
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

    # load list of prefixes dictionaries from file. Example:
    # "micro": [-6, "мк", "mk"] etc.
    with open('engine/data/units.json', 'r', encoding='utf8') as f:
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
        return Prefix(self.get_multiplier() - other.get_multiplier())

    def __str__(self):
        return f'{self.get_prefix_string()} | {self.get_multiplier()}'

    def __repr__(self):
        return str(self)


class MeasUnit:
    @staticmethod
    def init_from_file(data):
        type_of_unit = data[0]
        dataset = data[1:]
        base = MeasUnit.Fraction.base.value
        derived = MeasUnit.Fraction.derived.value
        numerator = MeasUnit.Fraction.numerator.value
        denominator = MeasUnit.Fraction.denominator.value

        if type_of_unit == base:
            base_unit = BaseMeasUnit.init_from_tokens(*dataset)
            d = {
                numerator: [base_unit],
                denominator: []
            }
            return DerivedMeasUnit(
                base_unit.get_symbol(),
                base_unit.get_category(),
                **d
            )
        elif type_of_unit == derived:
            return DerivedMeasUnit.init_from_tokens(*dataset)
        else:
            raise RuntimeError(f'incorrect type of unit to init: {type_of_unit}')

    with open('engine/data/units.json', 'r', encoding='utf8') as f:
        derived_units = json.load(f)['derived_units']

    with open('engine/data/units.json', 'r', encoding='utf8') as f:
        base_units = json.load(f)['base_units']

    with open('engine/data/units.json', 'r', encoding='utf8') as f:
        constants = json.load(f)['constants']

    class Fraction(enum.Enum):
        numerator = 'numerator'
        denominator = 'denominator'
        base = 'base'
        derived = 'derived'


# the unit of derived_unit with particular prefixes and degree
# Examples:
#   (m) || (mm) || (s) || (sm)^2
# P.S. you can see list of base_units in "units.json\base_units"
class BaseMeasUnit:
    @classmethod
    def init_from_tokens(
            cls,
            category: str,
            prefix: str,
            degree: int):
        return cls(prefix, category, degree)

    @classmethod
    def copy(cls, unit: BaseMeasUnit):
        prefix = unit.get_prefix().get_multiplier()
        category = unit.get_category()
        degree = unit.get_degree()
        return BaseMeasUnit(prefix, category, degree)

    def __init__(self,
                 prefix: str | int | Prefix,
                 category: str,
                 degree: int = 1,
                 multiplier: int = 0):
        data = MeasUnit.base_units[category]
        self.__category = category
        self.__symbol = data[0]
        self.__unit = data[1]
        self.__degree = degree * data[2]
        self.__prefix = Prefix('')
        self.__multiplier = multiplier
        self.set_prefix(prefix)

    def get_degree(self):
        return self.__degree

    def get_prefix(self):
        return self.__prefix

    def get_multiplier(self):
        return self.__multiplier

    def get_symbol(self):
        return self.__symbol

    def get_category(self):
        return self.__category

    def set_prefix(self, prefix: str | int | Prefix):
        prev_pref_mult = self.get_prefix().get_multiplier()
        self.__prefix = Prefix(prefix)
        n = prev_pref_mult - self.get_prefix().get_multiplier()
        self.__update_multiplier(n)

    def set_degree(self, n: float):
        self.__degree = n
        self.__multiplier = -self.get_multiplier()

    def to_si(self):
        if self.get_category() == 'mass':
            self.set_prefix('kilo')
        else:
            self.set_prefix("")

    def is_unit(self):
        return self.get_category() == 'unit'

    def __update_multiplier(self, n: int = None):
        if n is None:
            n = self.get_prefix().get_multiplier()
        self.__multiplier = self.get_multiplier() + n * self.__degree

    def __get_flipped(self):
        unit = BaseMeasUnit.copy(self)
        unit.set_degree(-unit.get_degree())
        return unit

    def __str__(self):
        s = ''
        # if self.get_multiplier() == 0:
        #     s = ''
        # else:
        #     s = f'10^[{self.get_multiplier()}] * '
        s = f'{s}{self.__prefix.get_prefix_string()}{self.__unit}'
        if self.get_degree() == 1:
            return s
        elif self.get_degree() == 0:
            return ''
        return f'{s}^[{self.get_degree()}]'

    def __repr__(self):
        return str(self)

    def __mul__(self, other: BaseMeasUnit):
        if self != other:
            raise RuntimeError(f'incorrect categories of multipliers')
        degree = self.get_degree() + other.get_degree()
        category = self.get_category()
        multiplier = self.get_multiplier() + other.get_multiplier()
        return BaseMeasUnit(Prefix(''), category, degree, multiplier)

    def __pow__(self, power: float):
        prefix = self.get_prefix()
        category = self.get_category()  # !&&!&!&!&!&!&^!@#%%@!$&TGU!FYDFUI !I
        degree = self.get_degree() * power
        unit = BaseMeasUnit(prefix, category, degree)
        return unit

    def __truediv__(self, other: BaseMeasUnit):
        other = other.__get_flipped()
        return self * other

    def __eq__(self, other: BaseMeasUnit):
        return self.get_category() == other.get_category()

    def __ne__(self, other: BaseMeasUnit):
        return not self == other


# the unit of derived_unit with particular prefixes
# Examples:
#   (m)/(s^2) || (mm)/(s^2),
#   (J) || (kg*m^2)/(s^2) <- physical work бирююююк
class DerivedMeasUnit:
    @classmethod
    def init_from_tokens(
            cls,
            category: str,
            index: int,
            prefixes: list):
        numerator = MeasUnit.Fraction.numerator.value
        denominator = MeasUnit.Fraction.denominator.value
        unit = MeasUnit.derived_units[category]
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
    def copy(cls, unit: DerivedMeasUnit):
        numerator = MeasUnit.Fraction.numerator.value
        denominator = MeasUnit.Fraction.denominator.value
        symbol = unit.get_symbol()
        category = unit.get_category()
        units = {numerator: [],
                 denominator: []}
        for un in unit.get_units()[numerator]:
            units[numerator].append(BaseMeasUnit.copy(un))
        for un in unit.get_units()[denominator]:
            units[denominator].append(BaseMeasUnit.copy(un))
        return cls(symbol, category, **units)

    def __init__(self, symbol: str, category: str, **units):
        numerator = MeasUnit.Fraction.numerator.value
        denominator = MeasUnit.Fraction.denominator.value
        self.__category = category
        self.__numerator = units[numerator]  # list if Kinds
        self.__denominator = units[denominator]  # list if Kinds
        self.__symbol = symbol
        self.__multiplier = 0
        self.__rel_multiplier = 0
        self.__update_multipliers(save_rel_multiplier=True)

    def get_units(self):
        numerator = MeasUnit.Fraction.numerator.value
        denominator = MeasUnit.Fraction.denominator.value
        d = {
            numerator: self.numerator(),
            denominator: self.denominator()
        }
        return d

    def numerator(self):
        return self.__numerator

    def denominator(self):
        return self.__denominator

    def get_multiplier(self):
        return self.__multiplier

    def get_rel_multiplier(self):
        return self.__rel_multiplier

    def get_symbol(self):
        return self.__symbol

    def get_category(self):
        return self.__category

    def set_prefix(self, unit: BaseMeasUnit, prefix: str):
        if unit in self.numerator():
            i = self.numerator().index(unit)
            self.__numerator[i].set_prefix(prefix)
        elif unit in self.denominator():
            i = self.denominator().index(unit)
            self.__denominator[i].set_prefix(prefix)
        else:
            raise RuntimeError(f"""No such unit ({str(unit)}) in {str(self)}""")
        self.__update_multipliers()

    def to_si(self):
        for unit in self.numerator():
            unit.to_si()
        for unit in self.__denominator:
            unit.to_si()
        self.__update_multipliers()

    def is_unit(self):
        v1 = not self.numerator() and not self.denominator()
        v2 = not self.denominator() and len(self.numerator()) == 1 and self.numerator()[0].is_unit()
        return v1 or v2

    def __get_flipped(self):
        unit = DerivedMeasUnit.copy(self)
        unit.__denominator, unit.__numerator = unit.__numerator, unit.__denominator
        return unit

    def __find_unit_in_fraction(self, unit: BaseMeasUnit):
        numerator = MeasUnit.Fraction.numerator.value
        denominator = MeasUnit.Fraction.denominator.value
        numer = self.numerator()
        denom = self.denominator()
        for i in range(len(numer)):
            if numer[i].get_category() == unit.get_category():
                return numerator, i
        for i in range(len(denom)):
            if denom[i].get_category() == unit.get_category():
                return denominator, i
        return False

    def __update_multipliers(self, save_rel_multiplier=False):
        multiplier = 0
        for unit in self.numerator():
            multiplier += unit.get_multiplier()
        for unit in self.denominator():
            multiplier -= unit.get_multiplier()
        if not save_rel_multiplier:
            self.__rel_multiplier += multiplier - self.__multiplier
        self.__multiplier = multiplier

    def __str__(self):
        if not self.numerator() and not self.denominator():
            return 'unit'
        if not self.denominator():
            return '*'.join(str(i) for i in self.numerator())
        if not self.numerator():
            return '[-1]*'.join(str(i) for i in self.numerator()) + '[-1]'
        s1 = '*'.join(str(i) for i in self.numerator())
        s2 = '*'.join(str(i) for i in self.denominator())
        return f'({s1})/({s2})'

    def __repr__(self):
        return str(self)

    def __mul__(self, other: DerivedMeasUnit):
        new_unit = DerivedMeasUnit.copy(self)
        numerator = MeasUnit.Fraction.numerator.value
        other_numer = other.numerator()
        other_denom = other.denominator()
        for i in range(len(other_numer)):
            find = new_unit.__find_unit_in_fraction(other_numer[i])
            if find:
                part = find[0]
                index = find[1]
                if part == numerator:
                    new_unit.__numerator[index] = new_unit.__numerator[index] * other_numer[i]
                else:
                    new_unit.__denominator[index] = new_unit.__denominator[index] / other_numer[i]
            else:
                new_unit.__numerator.append(other_numer[i])
        for i in range(len(other_denom)):
            find = new_unit.__find_unit_in_fraction(other_denom[i])
            if find:
                part = find[0]
                index = find[1]
                if part == numerator:
                    new_unit.__numerator[index] = new_unit.__numerator[index] / other_denom[i]
                else:
                    new_unit.__denominator[index] = new_unit.__denominator[index] * other_denom[i]
            else:
                new_unit.__denominator.append(other_denom[i])
        new_unit.__update_multipliers(save_rel_multiplier=True)
        return new_unit

    def __pow__(self, power: float):
        unit = DerivedMeasUnit.copy(self)
        numer = unit.numerator()
        denom = unit.denominator()
        numer_buf = []
        denom_buf = []
        for i in range(len(numer)):
            new_unit = numer[i] ** power
            if new_unit.get_degree() < 0:
                new_unit.set_degree(-new_unit.get_degree())
                del numer[i]
                denom_buf.append(new_unit)
            else:
                numer[i] = new_unit
        for i in range(len(denom)):
            new_unit = denom[i] ** power
            if new_unit.get_degree() < 0:
                new_unit.set_degree(-new_unit.get_degree())
                del denom[i]
                numer_buf.append(new_unit)
            else:
                denom[i] = new_unit
        numer.extend(numer_buf)
        denom.extend(denom_buf)
        return unit

    def __truediv__(self, other: DerivedMeasUnit):
        other = other.__get_flipped()
        return self * other

    def __eq__(self, other: DerivedMeasUnit):
        numer_1 = set(unit.get_category for unit in self.numerator())
        denom_1 = set(unit.get_category for unit in self.denominator())
        numer_2 = set(unit.get_category for unit in other.numerator())
        denom_2 = set(unit.get_category for unit in other.denominator())
        return numer_1 == numer_2 and denom_1 == denom_2

    def __ne__(self, other: DerivedMeasUnit):
        return not self == other
