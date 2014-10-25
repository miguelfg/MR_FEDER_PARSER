__author__ = 'miguelfg'

import os
import csv
import subprocess

PDF_INPUT_FOLDER = 'FEDER/PDF/regionales/'
TXT_INPUT_FOLDER = 'FEDER/TXT/'
CSV_OUTPUT_FOLDER = 'FEDER/CSV/'
HEADER_ROW = ['Nombre beneficiario', 'Nombre operación', 'Montante', 'pagado final', 'concesión/año']

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'

import logging

logging.basicConfig(format=FORMAT)
logger = logging.getLogger('scraper')
logger.setLevel('INFO')


class Parser():
    """
    Parser class for PDF files to TXT and CSV
    """
    def __init__(self):
        self.prev_row_item_length = 0
        self.prev_row_col1 = ''
        self.csv_filename = ''
        self.csv_lines = []

    def write_csv(self):
        logger.debug(CSV_OUTPUT_FOLDER + self.csv_filename)
        with open(CSV_OUTPUT_FOLDER + self.csv_filename, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=';',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADER_ROW)
            writer.writerows(self.csv_lines)


    # DONE BY SHELL SCRIPT!! -> parse_pdf_files.sh
    # def allPDFs2TXT():
    #     # subprocess.call('pdftotext -layout AR4214.pdf FEDER/TXT/AN4214.txt')
    #     for file in os.listdir(PDF_INPUT_FOLDER):
    #         if file.endswith('.pdf'):
    #             input_pdf_file = file
    #             output_txt_file = file.replace('.pdf', '.txt')
    #             input_path = PDF_INPUT_FOLDER + input_pdf_file
    #             output_path = TXT_INPUT_FOLDER + output_txt_file
    #
    #             # logger.debug(input_pdf_file)
    #             # logger.debug(output_txt_file)
    #             # logger.debug(input_path)
    #             # logger.debug(output_path)
    #             command = 'pdftotext -layout ' + input_path + ' ' + output_path
    #             # logger.debug('COMMAND TO EXECUTE: ' + command)
    #             logger.debug(command)
    #             # subprocess.call(command)
    #             # logger.debug('---------')

    def parse_txt_lines_before(self, line):
        pass

    def parse_csv_lines_after(self):
        pass

    def parse_data_line(self, line):
        line = line.split('  ')
        line = [l.strip() for l in line if l != '']

        if len(line) == 1:
            if self.prev_row_item_length == 4:
                line = [''] + line + ['', '', '']
            else:
                line = [''] + line

        elif len(line) == 3:
            logger.warn("------> 3 LINEAS " + '||'.join(line))

        elif len(line) == 4:
            # if self.prev_row_item_length == 5 or
            #     self.prev_row_item_length == 4:
            if self.prev_row_col1 == '':
                line = [''] + line
            else:
                line = [self.prev_row_col1] + line

        elif len(line) == 5:
            if line[0] != HEADER_ROW[0]:
                self.prev_row_col1 = line[0]
                logger.warn("------> 5 LINEAS " + '||'.join(line))
            else:
                line = None
        else:
            logger.warn("------> LEN OF LINE!!" + str(len(line)))

        return line

    def should_process_line(self, line):
        if line == '':
            logger.info("------> EMPTY_LINE @" + line)
            return None
        elif line == '\n':
            logger.info("------> EOL")
            return None
        elif 'Total beneficiario:' in line:
            logger.info("Total beneficiario:")
            return None
        elif 'Total beneficiario:' in line:
            logger.info("Total beneficiario:")
            return None
        elif 'Programa Operativo FEDER de' in line:
            logger.info("Programa Operativo FEDER del ")
            return None
        elif 'RELACIÓN DE OPERACIONES POR BENEFICIARIO' in line:
            logger.info("RELACIÓN DE OPERACIONES POR BENEFICIARIO")
            return None
        elif 'concedido' in line and 'operación' in line and 'del pago' in line:
            logger.info("------> concedido        operación          del pago")
            return None
        elif 'concedido        operación          del pago' in line:
            logger.info("------> concedido        operación          del pago")
            return None
        elif 'Año de la' in line:
            logger.info("------> Año de la")
            return None
        elif 'Programa operativo' in line:
            logger.info('------> LINEA PROGRAMA')
            return None
        elif 'de operaciones por beneficiario' in line:
            logger.info('------> LINEA PROGRAMA')
            return None
        elif '(Euros)' in line:
            logger.info('------> EUROS')
            return None

        return line

    def txt2csv(self, filename):
        file_path = TXT_INPUT_FOLDER + filename
        self.csv_filename = filename.replace('.txt', '.csv')
        logger.debug(file_path)

        with open(file_path, 'r') as f:
            content = f.readlines()
            logger.debug(len(content))

            # for line in content[:]:
            # for line in content[:500]:
            # for line in content[len(content) - 1000:]:
            for line in content[len(content) - 1000:len(content) - 800]:
                line = line.strip()
                if self.should_process_line(line) is not None:

                    parsed_line = self.parse_data_line(line)
                    if parsed_line is not None:
                        self.prev_row_item_length = len(line)
                        self.csv_lines.append(self.parse_data_line(line))
                    else:
                        self.prev_row_item_length = 0

            logger.debug(self.csv_lines)
            self.write_csv()

        logger.debug("===> END TXT FILE")



if __name__ == '__main__':

    # logger.debug("CURRENT DIR")
    # logger.debug(os.curdir)
    # logger.debug(os.listdir('FEDER/TXT'))
    # logger.debug(os.listdir('FEDER/PDF/regionales'))

    # parse all pdf files to txt
    # allPDFs2TXT()

    # parse all txt files to csv
    # pdftotext -layout input.pdf output.txt

    scraper = Parser()
    for filename in os.listdir(TXT_INPUT_FOLDER)[:1]:
        logger.debug('TXT2CSV: ' + filename)
        if filename.endswith('.txt'):
            scraper.txt2csv(filename)

