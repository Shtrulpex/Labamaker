class Kind:
    def __init__(self, name, multiple):
        self.name = name
        self.multiple = multiple

    def get_multiple(self):
        return self.multiple


class MeasUnit:
    def __init__(self, category, kind):
        self.category = category
        self.kind = kind

    def transform(self, new_kind):
        self.kind = new_kind

    def get_kind(self):
        return self.kind


class TextOption:
    def __init__(self, font, size, bold, color, italics, frame):
        self.font = font
        self.size = size
        self.bold = bold
        self.color = color
        self.italics = italics
        self.frame = frame


class ParamOption:
    def __init__(self, value, unit, name):
        self.value = value
        self.unit = unit
        self.name = name


class Parameter:
    def __init__(self, name, value, unit, option):
        self.name = name
        self.value = value
        self.unit = unit
        self.option = option

    def transform(self, new_unit):
        self.value *= self.unit.get_kind().get_multiple() / new_unit.get_kind().get_multiple()
        self.unit = new_unit
