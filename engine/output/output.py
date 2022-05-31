from pylatex import Document, Section, Subsection, Tabular
from pylatex import Math, Alignat, Itemize, Command
from pylatex.utils import italic, bold

from engine.data.data import *


class Template:
    def __init__(self,
                 lab: str,
                 data_result: DataResult,
                 geometry_options=None
                 ):
        if geometry_options is None:
            geometry_options = {"tmargin": "1.5cm", "lmargin": "2cm", "rmargin": "2cm"}
        self.__geomytry_options = geometry_options
        self.__doc = Document(geometry_options=geometry_options)
        self.data_result = data_result
        self.result_path = None
        self.result_filename = None
        self.__load_template(lab)

    def get_pdf(self):
        self.__fill()
        self.__generate_pdf()

    def __fill(self):
        doc = self.__doc
        images = self.data_result.get_images_dict()
        parameters = self.data_result.get_parameters_dict()
        tables = self.data_result.get_tables_dict()

        pi = 3.14
        r = 2
        with doc.create(Section(bold('Data Processing'))):
            with doc.create(Itemize()) as itemize:
                itemize.add_item('Wire resistivity: ')
                with doc.create(Alignat(numbering=False, escape=False)) as agn:
                    agn.append(r'\rho =\frac{RS}{l}')
                itemize.add_item('Wire section area')
                with doc.create(Alignat(numbering=False, escape=False)) as agn:
                    agn.append(r'S=\frac{\pi d^2}{4}')
            with doc.create(Subsection(bold('Wire section area'))):
                with doc.create(Alignat(numbering=False, escape=False)) as agn:
                    agn.append(r'S=\frac{\pi d^2}{4}=')
                    s = f'{r}^2'
                    agn.append(fr'\frac{pi}{s}')

            with doc.create(Subsection(bold('Turn length'))):
                pass

            with doc.create(Subsection(bold('LSM'))):
                with doc.create(Alignat(numbering=False, escape=False)) as agn:
                    agn.append(r'{R_n}=\frac{\rho l}{S} n=k x + b\\')
                    agn.append(italic(r'b=0'))

    def __generate_pdf(self):
        current_file = os.getcwd()
        os.chdir(self.result_path)
        self.__doc.generate_pdf(self.result_filename, clean_tex=True)
        os.chdir(current_file)

    # load template from file!!!!
    # and set Template attributes:
    #   - self.result_path
    #   - self.result_filename
    def __load_template(self, lab: str):
        self.result_path = './results/lab_111'
        self.result_filename = 'lab_111_result'
