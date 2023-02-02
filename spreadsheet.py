import csv
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import PatternFill


class Spreadsheet:
    #  This will take the spreadsheet of top containers and parse them for aspace and write the spreadsheet template
    #      data to the template
    pass

    @staticmethod
    def get_barcodes(tc_spreadsheet):
        """
        Intakes a spreadsheet and returns a list of barcodes

        :param tc_spreadsheet: spreadsheet object of top containers for retrieving barcodes

        :return list barcodes: list of barcodes (str) for top containers
        """
        barcodes = []
        with open(tc_spreadsheet, newline='') as csvfile:
            test_reader = csv.reader(csvfile)
            column_num = 0
            barcode_col = None
            for row in test_reader:
                for value in row:
                    if value == "barcode_u_sstr":
                        barcode_col = column_num
                        # print(column_num)
                        pass
                    else:
                        column_num += 1
                # print(row)
                barcodes.append(row[barcode_col])
            barcodes.pop(0)
        return barcodes

    def write_template(self):
        # fill in here when we need to write data to DLG template spreadsheet
        pass

        # tc_wb = load_workbook(tc_spreadsheet, data_only=True)
        # print(tc_wb)
        # for row in tc_wb:
        #     print(row)
