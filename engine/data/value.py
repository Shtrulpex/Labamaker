from __future__ import annotations

class Value:
    def __init__(self, value: float | None = None, rel_err: float | None = None, multiplier: int = 0):
        self.__value = None
        self.__abs_err = None
        self.__rel_err = None
        self.__multiplier = multiplier
        if value is not None:
            self.__value = value
            self.set_multiplier(multiplier)
        if rel_err is not None:
            self.__abs_err = value * rel_err
            self.__rel_err = rel_err

    def get_value(self):
        return self.__value

    def get_multiplier(self):
        return self.__multiplier

    def get_abs_err(self):
        return self.__abs_err

    def get_rel_err(self):
        return self.__rel_err
    
    def set_multiplier(self, n: int):
        self.__value *= 10 ** self.get_multiplier()
        if self:
            self.__abs_err *= 10 ** self.get_multiplier()
        self.__multiplier = n
        self.__value /= 10 ** self.get_multiplier()
        if self:
            self.__abs_err /= 10 ** self.get_multiplier()

    @staticmethod
    def __count_rel_err(action: str, first: Value, second: Value | float, *res_value):  # '*', '/', '+', '-', '**'
        if action == '*' or action == '/':
            if not first and not second:
                rel_err = None
            elif first:
                rel_err = first.get_rel_err()
            elif second:
                rel_err = second.get_rel_err()
            else:
                rel_err = (first.get_rel_err() ** 2 + second.get_rel_err() ** 2) ** 0.5
        elif action == '+' or action == '-':
            if not first and not second:
                rel_err = None
            elif first:
                rel_err = first.get_rel_err()
            elif second:
                rel_err = second.get_rel_err()
            else:
                abs_err_sq = first.get_abs_err() ** 2 + second.get_abs_err() ** 2
                rel_err = (abs_err_sq / res_value[0] ** 2) ** 0.5
        elif action == '**':
            power = second
            if not first:
                rel_err = None
            else:
                rel_err = abs(power) * first.get_rel_err()
        else:
            raise RuntimeError(f'incorrect action with values: {action}')
        return rel_err

    def __bool__(self):
        return self.get_rel_err() is not None

    def __str__(self):
        s = f'{self.get_value()}'
        if self:  # rel_err is not None
            s += f' ± {str(self.get_abs_err())}'
        return s

    def __repr__(self):
        return str(self)

    # self / 10^n (n > 0)
    # Example:
    #   1.3 << 2 -> 0.013 * 10^2
    def __lshift__(self, n: int):
        self.set_multiplier(self.get_multiplier() + n)

    # self / 10^n (n > 0)
    # Example:
    #   1.3 >> 3 -> 0.013 * 10^3
    def __rshift__(self, n: int):
        self.set_multiplier(self.get_multiplier() - n)

    def __mul__(self, other: Value | float):
        if type(other) == Value:
            value = self.get_value() * other.get_value()
            multiplier = self.get_multiplier() + other.get_multiplier()
            rel_err = Value.__count_rel_err('*', self, other)
        else:
            value = self.get_value() * other
            multiplier = self.get_multiplier()
            # rel_err = Value.__count_rel_err('*', self, other)
            rel_err = self.get_rel_err()
        return Value(value, rel_err, multiplier=multiplier)

    def __truediv__(self, other: Value):
        value = self.get_value() / other.get_value()
        multiplier = 10 ** self.get_multiplier() / 10 ** other.get_multiplier()
        rel_err = Value.__count_rel_err('/', self, other)
        return Value(value, rel_err, multiplier=multiplier)

    def __add__(self, other: Value):
        value = self.get_value() * 10 ** self.get_multiplier() + other.get_value() * 10 ** other.get_multiplier()
        rel_err = Value.__count_rel_err('+', self, other, value)
        return Value(value, rel_err)

    def __sub__(self, other: Value):
        value = self.get_value() * 10 ** self.get_multiplier() - other.get_value() * 10 ** other.get_multiplier()
        rel_err = Value.__count_rel_err('-', self, other, value)
        return Value(value, rel_err)

    def __pow__(self, power: float):
        value = self.get_value() ** power
        multiplier = -self.get_multiplier()
        rel_err = Value.__count_rel_err('**', self, power)
        return Value(value, rel_err, multiplier=multiplier)
