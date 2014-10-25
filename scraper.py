# -*- coding: utf-8 -*-
__author__ = 'miguelfg'

import os
import csv
from datetime import datetime
import subprocess
import collections
compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

PDF_INPUT_FOLDER = 'FEDER/PDF/regionales/'
TXT_INPUT_FOLDER = 'FEDER/TXT/'
CSV_OUTPUT_FOLDER = 'FEDER/CSV/'
HEADER_ROW = ['Nombre beneficiario', 'Nombre operación', 'Montante', 'pagado final', 'concesión/año']

FORMAT = '%(asctime)-15s %(levelname)s %(message)s'

import logging

logging.basicConfig(format=FORMAT)
logger = logging.getLogger('scraper')
# logger.setLevel('INFO')
# logger.setLevel('DEBUG')
# logger.setLevel('ERROR')
logger.setLevel('CRITICAL')


class Parser():
    """
    Parser class for PDF files to TXT and CSV
    """
    def __init__(self):
        self.prev_row_item_length = 0
        self.prev_row_col1 = ''
        self.prev_row = []
        self.csv_filename = ''
        self.csv_lines = []

    def write_csv(self):
        logger.critical(CSV_OUTPUT_FOLDER + self.csv_filename)
        logger.critical("====> NUMBER OF LINES IN CSV:" + str(len(self.csv_lines)))
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

    def duplicate_with_next_row(self, line, next_line):
        return compare(line, next_line)

    def parse_csv_lines_after(self):
        # for line in self.csv_lines:
        indexes_to_remove = []
        for i in range(len(self.csv_lines)):
            line = self.csv_lines[i]
            if len(line) != 5:
                logger.error("LEN LINE : " + str(len(line)) + " " + line[0])
            else:
                try:
                    next_line = self.csv_lines[i+1]
                    if self.duplicate_with_next_row(line[1:], next_line[1:]):
                        # we found a duplicate
                        # logger.critical("DUPLICATE: " + '||'.join(line))
                        # logger.critical("DUPLICATE: " + '||'.join(next_line))
                        # self.csv_lines.pop(i+1)
                        indexes_to_remove.append(i+1)
                        # pass
                except IndexError:
                    logger.critical("EOF ??: " + str(len(line)) + " == " + str(i))

        for r in reversed(indexes_to_remove):
            self.csv_lines.pop(r)

    def parse_data_line(self, line):
        line = line.split('  ')
        line = [l.strip() for l in line if l != '']

        if len(line) == 1:
            logger.error("------> 1 LINEAS @ " + str(self.prev_row_item_length) + ' ' + '||'.join(line))
            if self.prev_row_item_length == 4:
                # line = [''] + line + ['', '', '']
                new_col = ' '.join([self.prev_row[1], line[0]])
                line = self.prev_row[:1] + [new_col] + self.prev_row[2:]
                logger.error("------> 1 LINEAS CON PREV 4 ----> " + '||'.join(line))
            elif self.prev_row_item_length == 5:
                # logger.error("------> 1 LINEAS CON PREV 5" + '||'.join(self.prev_row))
                new_col = ' '.join([self.prev_row[0], line[0]])
                line = [new_col] + self.prev_row[1:]
                logger.error("------> 1 LINEAS CON PREV 5 ----> " + '||'.join(line))
            else:
                line = [''] + line

        elif len(line) == 3:
            logger.warn("------> 3 LINEAS " + '||'.join(line))

        elif len(line) == 4:
            if self.prev_row_col1 == '':
                line = [''] + line
            else:
                line = [self.prev_row_col1] + line
            self.prev_row = line

        elif len(line) == 5:
            if line[0] != HEADER_ROW[0]:
                self.prev_row_col1 = line[0]
                logger.info("------> 5 LINEAS " + '||'.join(line))
            else:
                logger.debug("------> 5 LINEAS " + '||'.join(line))
                line = None
            self.prev_row = line

        else:
            logger.error("------> LEN OF LINE!!" + str(len(line)))

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
        elif 'Total operaciones de ' in line:
            logger.info("Total operaciones de ")
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

            for line in content[:]:
            # for line in content[:3000]:
            # for line in content[:500]:
            # for line in content[len(content) - 1000:]:
            # for line in content[len(content) - 1000:len(content) - 800]:
                line = line.strip()
                if self.should_process_line(line) is not None:

                    parsed_line = self.parse_data_line(line)
                    if parsed_line is not None:
                        self.prev_row_item_length = len(parsed_line)
                        self.csv_lines.append(self.parse_data_line(line))
                    else:
                        self.prev_row_item_length = 0

        logger.debug("===> END TXT FILE")



if __name__ == '__main__':
    start_time = datetime.now()
    print("START TIME:", start_time)

    # logger.debug("CURRENT DIR")
    # logger.debug(os.curdir)
    # logger.debug(os.listdir('FEDER/TXT'))
    # logger.debug(os.listdir('FEDER/PDF/regionales'))

    # parse all pdf files to txt
    # allPDFs2TXT()

    # parse all txt files to csv
    # pdftotext -layout input.pdf output.txt

    for filename in os.listdir(TXT_INPUT_FOLDER)[:]:
        scraper = Parser()
        logger.debug('TXT2CSV: ' + filename)
        if filename.endswith('.txt'):
            scraper.txt2csv(filename)
            scraper.parse_csv_lines_after()
            scraper.write_csv()

    print("END TIME:", datetime.now())
    print("DURATION TIME:", datetime.now() - start_time)