# Здесь нужно написать класс текста, с которым
# модно будет работать по тем же принципам, что и с
# таблицами и параметрами, а также удобно заполнять шаблоны для
# итогового представления результата

from engine.data.option import *


class Text:
    def __init__(self, text: str = '',
                 kind: str = TextKinds.default.value,
                 **params):
        self.text = text
        self.kind = kind  # text/formula/list/title
        self.options = TextOption(kind=kind, **params)
