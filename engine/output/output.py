from pylatex import Document, Section, Subsection, Tabular
from pylatex import Math, Alignat, Itemize, Command
from pylatex.utils import italic, bold

import shutil


class Template:
    def __init__(self,
                 result_path: str,
                 geometry_options=None
                 ):
        if geometry_options is None:
            geometry_options = {"tmargin": "1.5cm", "lmargin": "2cm", "rmargin": "2cm"}
        self.__geomytry_options = geometry_options
        self.__doc = Document(geometry_options=geometry_options)
        self.result_path = result_path
        self.number_of_parameters = None
        self.parameters = None
        self.__load_template('')

    def fill(self, **kwargs):
        r = 2
        pi = 3.14
        if len(kwargs) != self.number_of_parameters:
            raise RuntimeError(f'Incorrect number of parameters to write in PDF')
        doc = self.__doc
        with doc.create(Section(bold('Data Processing'))):
            with doc.create(Itemize()) as itemize:
                itemize.add_item('Wire resistivity: ')
                with doc.create(Alignat(numbering=False, escape=False)) as agn:
                    agn.append(r'{\rho}=\frac{RS}{l}')
            with doc.create(Subsection(bold('Wire section area'))):
                with doc.create(Alignat(numbering=False, escape=False)) as agn:
                    agn.append(r'S=\pi r^2=')
                    s = f'{r}^2'
                    agn.append(fr'\frac{pi}{s}')

            with doc.create(Subsection(bold('Turn length'))):
                pass

            with doc.create(Subsection(bold('LSM'))):
                with doc.create(Alignat(numbering=False, escape=False)) as agn:
                    agn.append(r'{R_n}=\frac{\rho l}{S} n=k x + b\\')
                    agn.append(italic(r'b=0'))

    def generate_pdf(self, filename):
        self.__doc.generate_pdf(filename, clean_tex=True)
        # shutil.move(__file__ + '\\' + filename, self.result_path)

    # load template from file,
    # set Template attributes:
    #   - number_of_parameters
    #   - self.parameters
    def __load_template(self, file: str):
        self.number_of_parameters = 0
        self.parameters = {}


tmp = Template(__file__)
tmp.fill()
tmp.generate_pdf('new_full')
