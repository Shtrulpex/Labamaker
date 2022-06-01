import json

from engine.enums import TextKinds


class Option:
    with open('engine/data/text_options.json', 'r', encoding='utf8') as f:
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


class ParamOptions(Option):
    @classmethod
    def default_init(cls, rel_err=False):
        kwargs = {'value': dict(),
                  'unit': dict(),
                  'name': dict(),
                  'symbol': dict()}
        if rel_err:
            kwargs['absolute_error'] = dict()
            kwargs['relative_error'] = dict()
        return cls(**kwargs)

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
