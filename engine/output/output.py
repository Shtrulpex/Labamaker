from pylatex import Document, Section, Subsection, Tabular
from pylatex import Alignat, Itemize, Figure
from pylatex.utils import italic, bold, NoEscape
import os
from engine.data.data import *


def to_fixed(num: float, digits=3):
    return f"{num:.{digits}f}"


class Template:
    def __init__(self,
                 lab: str,
                 geometry_options=None
                 ):
        if geometry_options is None:
            geometry_options = {"tmargin": "1.5cm", "lmargin": "2cm", "rmargin": "2cm"}
        self.__geomytry_options = geometry_options
        self.__doc = Document(geometry_options=geometry_options)
        self.result_path = None
        self.result_filename = None
        self.__load_template(lab)

    def write_pdf(self, **kwargs):
        self.__fill(**kwargs)
        self.__generate_pdf()

    def __fill(self, **kwargs):
        doc = self.__doc
        images = kwargs['images']
        parameters = kwargs['parameters']
        tables = kwargs['tables']

        def write_res(alignant, parameter: Parameter, digit=3, shift=True, abs_err=0):
            if shift:
                alignant.append(fr'{to_fixed(parameter.get_value())} \pm')
                alignant.append(fr'{to_fixed(parameter.get_abs_err(), digits=digit)}')
                alignant.append(fr'{parameter.get_unit()}\\')
                alignant.append(fr'\sigma({parameter.get_symbol()}) ='
                                fr'{to_fixed(parameter.get_rel_err() * 100, digits=2)} \% \\')
            else:
                alignant.append(fr'{to_fixed(parameter.get_value())} \pm')
                alignant.append(fr'{to_fixed(abs_err.get_value())}')
                alignant.append(fr'{parameter.get_unit()}\\')


        pi = 3.14
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
                    d2 = f'{to_fixed(parameters["wire_diameter"].get_value(), digits=2)}^2'
                    pi_d2 = fr'{pi}*{d2}'
                    agn.append(fr'{pi_d2} / 4=')
                    cq = parameters["circle_square"]
                    write_res(agn, cq)

            with doc.create(Subsection(bold('Turn length'))):
                with doc.create(Alignat(numbering=False, escape=False)) as agn:
                    L = parameters["length_of_the_drum_section_with_the_wire"]
                    n = parameters["total_number_of_turns"]
                    step = parameters["step"]
                    tl = parameters["circle_length_with_step"]
                    cl = parameters["circle_length"]
                    D = parameters["reochord_drum"]
                    h = parameters["groove_depth"]

                    agn.append(r'l_{step}=\frac{L}{N}=')
                    agn.append(fr'{L.get_value()}/{n.get_value()}=')
                    write_res(agn, step)
                    agn.append(r'l_{circle}=\pi (D-2h)=')
                    agn.append(fr'{pi}*({to_fixed(D.get_value())}-2{to_fixed(h.get_value())})=')
                    write_res(agn, cl)
                    agn.append(r'l_{turn}=\sqrt{(l_(circle))^2+(l_(step))^2}=')
                    a, b = f'{to_fixed(cl.get_value())}^2', f'{to_fixed(step.get_value())}^2'
                    agn.append(fr'\sqrt ({a + "+" + b})=')
                    write_res(agn, tl)

            with doc.create(Subsection(bold('LSM'))):
                with doc.create(Alignat(numbering=False, escape=False)) as agn:
                    k = parameters["mls_koef_k"]
                    dk = parameters["k_error"]

                    agn.append(r'{R_n}=\frac{\rho l}{S} n=k x + b\\')
                    agn.append(italic(r'b=0'))
                    agn.append(r'\\k=\frac{<{R_n}> - <n><{R_n}>}{<n^2> - <n>^2}=')
                    write_res(agn, k, shift=False, abs_err=dk)

            with doc.create(Subsection(bold('Resistivity'))):
                with doc.create(Alignat(numbering=False, escape=False)) as agn:
                    p = parameters['resistivity']
                    k = parameters['mls_koef_k']
                    s = parameters['circle_square']
                    l = parameters['circle_length_with_step']

                    agn.append(r'\rho=\frac{S*a}{l}=')
                    agn.append(fr'{to_fixed(s.get_value())} * {to_fixed(k.get_value())}/{to_fixed(l.get_value())}=')
                    write_res(agn, p, digit=7)

            with doc.create(Figure(position='htbp')) as graphic:
                image_filename = str(os.getcwd() + '\\' + images['graph'])
                graphic.add_image(image_filename)
                graphic.add_caption('R(N)')

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
