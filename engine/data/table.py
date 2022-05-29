from __future__ import annotations
import pandas as pd
import numpy as np

from measunit import MeasUnit


class Table:
    @classmethod
    def init_from_file(cls, name: str, data: dict):
        row_headers = data['row_headers']
        column_headers = data['column_headers']
        table = np.array(data['table'])
        table = np.insert(table, 0, values=column_headers, axis=1)
        df = pd.DataFrame(table,
                          columns=row_headers,
                          index=column_headers)
        units = []
        for unit in data['units']:
            if unit:
                units.append(MeasUnit.init_from_file(unit))
        return cls(name, units, df)

    def __init__(self,
                 name: str,
                 units: list,
                 data_frame: pd.DataFrame):
        self.__name = name
        self.__table = data_frame  # dataframe of Parameters
        self.__units = units  # list of Units

    def get_name(self):
        return self.__name

    def get_table(self):
        return self.__table

    def to_csv(self, file: str):
        self.__table.to_csv(file)

    def transpose(self):
        self.__table.transpose()

    def shape(self):
        return self.__table.shape

    def height(self):
        return self.shape()[0]

    def width(self):
        return self.shape()[1]

    def __getitem__(self, key: str | int):
        return self.__table[key]

    def __setitem__(self, key: str | int, value: pd.Series):
        self.__table[key] = value
