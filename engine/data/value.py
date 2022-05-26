from __future__ import annotations


class Value:
    def __init__(self, value: float | None, rel_err: float | None, multiplier: float = 1):
        self.value = value
        self.multiplier = multiplier
        self.abs_err = None
        self.rel_err = None
        if rel_err is not None:
            self.abs_err = value * rel_err
            self.rel_err = rel_err

    def get_value(self):
        return self.value * self.multiplier

    def get_abs_err(self):
        return self.abs_err

    def get_rel_err(self):
        return self.rel_err

    def __bool__(self):
        return bool(self.rel_err)

    def __mul__(self, other: Value):
        value = self.value * other.value
        multiplier = self.multiplier * other.multiplier
        rel_err = Value.__count_rel_err('*', self, other)
        return Value(value, rel_err, multiplier=multiplier)

    def __truediv__(self, other: Value):
        value = self.value / other.value
        multiplier = self.multiplier / other.multiplier
        rel_err = Value.__count_rel_err('/', self, other)
        return Value(value, rel_err, multiplier=multiplier)

    def __add__(self, other: Value):
        value = self.value * self.multiplier + self.value * self.multiplier
        rel_err = Value.__count_rel_err('+', self, other, value)
        return Value(value, rel_err)

    def __sub__(self, other: Value):
        value = self.value * self.multiplier + self.value * self.multiplier
        rel_err = Value.__count_rel_err('-', self, other, value)
        return Value(value, rel_err)

    def __pow__(self, power):
        value = self.value ** power
        multiplier = self.multiplier ** power
        rel_err = Value.__count_rel_err('**', self, power)
        return Value(value, rel_err, multiplier=multiplier)

    def __str__(self):
        return self.__get_value_string()

    def __repr__(self):
        return str(self)

    def __get_value_string(self):
        if self.abs_err:
            s = f'{self.value} ± {str(self.abs_err)}'
        else:
            s = f'{self.value}'
        return s

    @staticmethod
    def __count_rel_err(action: str, first: Value, second: Value | float, *res_value):  # '*', '/', '+', '-', '**'
        rel_err = None
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
                rel_err = power * first.get_rel_err()
        else:
            raise RuntimeError(f'incorrect action with values: {action}')
        return rel_err
