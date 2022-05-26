import pandas as pd


class Table:
    def __init__(self, name: str, file: str):
        self.name = name.split('.')[0]
        if name.endswith('.csv'):
            self.table = pd.read_csv(file, index_col=0)

    def convert(self):
        pass
