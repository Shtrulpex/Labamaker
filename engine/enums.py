from enum import Enum, auto


class Data(Enum):
    X = auto()
    Y = auto()
    K = auto()
    B = auto()
    DK = auto()
    DB = auto()
    RESULT = auto()
    S = auto()
    L = auto()
    D = auto()
    P = auto()
    l = auto()
    d = auto()
    N = auto()
    STEP = auto()
    h = auto()
    lc = auto()


class GraphType(Enum):
    MLS = auto()
    BAR = auto()


class TextKinds(Enum):
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
