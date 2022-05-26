from __future__ import annotations

from measunit import *
from option import *
from value import *


class Parameter:
    @staticmethod
    def mul(first: Parameter, second: Parameter, name: str):
        parameter = first * second
        parameter.set_name(name)
        return parameter

    @staticmethod
    def div(first: Parameter, second: Parameter, name: str):
        parameter = first / second
        parameter.set_name(name)
        return parameter

    @staticmethod
    def add(first: Parameter, second: Parameter, name: str):
        parameter = first + second
        parameter.set_name(name)
        return parameter

    @staticmethod
    def sub(first: Parameter, second: Parameter, name: str):
        parameter = first - second
        parameter.set_name(name)
        return parameter

    @classmethod
    def init_parameter_from_file(cls, **data):
        name = data['name']
        symbol = data['symbol']
        value = data['value']
        unit = data['unit']
        options = data['options']
        multiplier = 1
        if 'multiplier' in data.keys():
            multiplier = data['multiplier']
        if 'absolute_error' in data.keys():
            abs_err = data['absolute_error']
            rel_err = abs_err / value
        else:
            abs_err = None
            rel_err = None
        return cls(
            Value(value, rel_err, multiplier=multiplier),
            MeasUnit.init_from_file(unit),
            ParamOptions(**options),
            symbol,
            name
        )

    def __init__(self,
                 value: Value,
                 unit: MeasUnit,
                 options: ParamOptions,
                 symbol,
                 *name
                 ):
        self.__name = ''
        if name:
            self.__name = name[0]
        self.__value = value
        self.__unit = unit
        self.__options = options
        self.__symbol = 'something'
        if symbol:
            self.__symbol = symbol

    def get_value(self):
        return self.__value

    def get_symbol(self):
        return self.__symbol

    def get_options(self):
        return self.__options

    def get_unit(self):
        return self.__unit

    def get_name(self):
        return self.__name

    def set_name(self, name: str):
        self.__name = name

    def to_si(self):
        pass

    def convert(self):
        pass

    def __get_param_string(self):
        return f'{self.get_symbol()} = {self.get_value()} {self.get_unit()}'

    def __flip(self):
        value = self.get_value() ** -1
        unit = self.get_unit() ** -1
        options = self.get_options()
        symbol = self.get_symbol() + '^[-1]'
        parameter = Parameter(value, unit, options, symbol, symbol)
        return parameter

    def __str__(self):
        return self.__get_param_string()

    def __repr__(self):
        return f'{self.get_name()}: [{self}]'

    def __mul__(self, other: Parameter) -> Parameter:
        value = self.get_value() * other.get_value()
        unit = self.get_unit() * other.get_unit()
        options = self.get_options()
        symbol = self.get_symbol() + other.get_symbol()
        parameter = Parameter(value, unit, options, symbol, symbol)
        return parameter

    def __truediv__(self, other: Parameter):
        other = other.__flip()
        return self * other

    def __add__(self, other: Parameter):
        if self.get_unit() != other.get_unit():
            raise RuntimeError(f'incorrect units to add')
        value = self.get_value() + other.get_value()
        unit = self.get_unit()
        options = self.get_options()
        symbol = self.get_symbol()
        parameter = Parameter(value, unit, options, symbol, symbol)
        return parameter

    def __sub__(self, other: Parameter):
        if self.get_unit() != other.get_unit():
            raise RuntimeError(f'incorrect units to add')
        value = self.get_value() - other.get_value()
        unit = self.get_unit()
        options = self.get_options()
        symbol = self.get_symbol()
        parameter = Parameter(value, unit, options, symbol, symbol)
        return parameter

    def __pow__(self, power: float):
        value = self.get_value() ** power
        unit = self.get_unit() ** power
        options = self.get_options()
        symbol = f'{self.get_symbol()}^[{power}]'
        parameter = Parameter(value, unit, options, symbol, symbol)
        return parameter
