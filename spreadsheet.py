import csv
from pathlib import Path
from openpyxl import load_workbook, utils
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

    @staticmethod
    def write_template(aspace_dlg_template, arch_obj, row_number):
        data_columns = {}
        temp_wb = load_workbook(aspace_dlg_template)
        for sheet in temp_wb:
            for row in sheet.iter_rows(max_row=1, max_col=27):
                for header in row:  # TODO - check if there are headers - don't want to write to blank sheet
                    # column_index = header.column
                    data_columns[header.value] = utils.coordinate_to_tuple(header.coordinate)
                    # column_index += 1
                    # row_index = header.row
            for column, coordinate in data_columns.items():
                if "dcterms_title" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.title
                if "dcterms_creator" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.creator
                if "dcterms_subject" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.subject
                if "dcterms_description" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.description
                if "dc_date" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.date
                if "dcterms_spatial" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.subject_spatial
                if "dcterms_medium" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.subject_medium
                if "extent" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.extent
                if "dcterms_language" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.language
                if "dcterms_bibliographic_citation" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.citation
                if "dlg_subject_personal" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.subject_personal
                if "holding institution" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = "Hargrett Library"
                if "public" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = "true"
        temp_wb.save(aspace_dlg_template)



        # print(temp_wb.sheetnames)
