from __future__ import annotations

from value import *
from measunit import *
from option import *


class Parameter:
    @staticmethod
    def mul(first: Parameter, second: Parameter | float, name: str):
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

    @staticmethod
    def pow(first: Parameter, power: float, name: str):
        parameter = first ** power
        parameter.set_name(name)
        return parameter

    @classmethod
    def init_from_file(cls, name: str, data: dict):
        symbol = data['symbol']
        value = data['value']
        unit = data['unit']
        options = data['options']
        multiplier = 0
        if 'multiplier' in data.keys():
            multiplier = data['multiplier']
        if 'absolute_error' in data.keys():
            abs_err = data['absolute_error']
            if abs_err is None:
                rel_err = None
            else:
                rel_err = abs_err / value
        else:
            rel_err = None
        return cls(
            Value(value, rel_err, multiplier=multiplier),
            MeasUnit.init_from_file(unit),
            symbol,
            name,
            options=ParamOptions(**options)
        )

    def __init__(self,
                 value: Value,
                 unit: DerivedMeasUnit,
                 symbol,
                 *name,
                 options: ParamOptions = ParamOptions.default_init(bool(Value))
                 ):
        self.__name = ''
        if name:
            self.__name = name[0]
        self.__value = value
        self.__unit = unit
        self.__options = options
        self.__symbol = 'something'
        self.__update_multiplier()
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

    def get_unit_numerator(self):
        return self.__unit.numerator()

    def get_unit_denominator(self):
        return self.__unit.denominator()

    def get_multiplier(self):
        return self.__multiplier

    def get_name(self):
        return self.__name

    def set_name(self, name: str):
        self.__name = name

    def set_symbol(self, symbol: str):
        self.__symbol = symbol

    def set_prefix(self, unit: BaseMeasUnit, prefix: str):
        self.__unit.set_prefix(unit, prefix)
        self.__update_multiplier()

    def to_si(self):
        self.__unit.to_si()
        self.__update_multiplier()

    def to_json(self, file: str):
        pass

    def __update_multiplier(self):
        self.__multiplier = self.get_value().get_multiplier() +\
                            self.get_unit().get_rel_multiplier()

    @staticmethod
    def __get_flipped(obj):
        if type(obj) == Parameter:
            if obj.get_value() == 0:
                raise RuntimeError(f'Division by zero: {obj.get_name()}: {obj.get_symbol()} = 0')
            value = obj.get_value() ** -1
            unit = obj.get_unit() ** -1
            options = obj.get_options()
            symbol = obj.get_symbol() + '^[-1]'
            parameter = Parameter(value, unit, symbol, symbol, options=options)
            return parameter
        elif type(obj) in (int, float):
            if obj == 0:
                raise RuntimeError(f'Division by zero')
            return 1 / obj

    @staticmethod
    def __action(first: Parameter, second: Parameter | float | int, action: str):  # '+', '-', '*', '**'
        if action in ('+', '-'):
            if bool(first.get_unit()) != bool(second.get_unit()):
                raise RuntimeError(f'incorrect units to add')
            if action == '+':
                value = first.get_value() + second.get_value()
            else:
                value = first.get_value() - second.get_value()
            unit = first.get_unit()
            options = first.get_options()
            symbol = first.get_symbol()
            parameter = Parameter(value, unit, symbol, symbol, options=options)
            return parameter
        elif action == '*':
            if type(second) == Parameter:
                value = first.get_value() * second.get_value()
                unit = first.get_unit() * second.get_unit()
                symbol = first.get_symbol() + second.get_symbol()
            elif type(second) in (float, int):
                value = first.get_value() * second
                unit = first.get_unit()
                symbol = first.get_symbol()
            else:
                raise RuntimeError(f'Incorrect operators of mul:'
                                   f'Parameter and {type(second)}')
            options = first.get_options()
            parameter = Parameter(value, unit, symbol, symbol, options=options)
            return parameter
        elif action == '**':
            power = second
            value = first.get_value() ** power
            unit = first.get_unit() ** power
            options = first.get_options()
            symbol = f'{first.get_symbol()}^[{power}]'
            parameter = Parameter(value, unit, symbol, symbol, options=options)
            return parameter
        else:
            raise RuntimeError(f'Incorrect action to do: {action}')

    def __str__(self):
        s = ' '
        if self.get_multiplier() != 0:
            s = f' * 10^[{self.get_multiplier()}] '
        return f'{self.get_symbol()} = {self.get_value()}{s}{self.get_unit()}'

    def __repr__(self):
        return f'{self.get_name()}: [{self}]'

    def __mul__(self, other: Parameter | float | int) -> Parameter:
        return Parameter.__action(self, other, '*')

    def __truediv__(self, other: Parameter | float | int):
        other = Parameter.__get_flipped(other)
        return self * other

    def __add__(self, other: Parameter):
        return Parameter.__action(self, other, '+')

    def __sub__(self, other: Parameter):
        return Parameter.__action(self, other, '-')

    def __pow__(self, power: float):
        return Parameter.__action(self, power, '**')

    def __rshift__(self, n: int):
        self.__value >> n
        self.__update_multiplier()

    def __lshift__(self, n: int):
        self.__value << n
        self.__update_multiplier()
