import csv
from loguru import logger
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
        """
        Intakes the aspace_dlg spreadsheet and writes data from archival object instance row by row

        :param str aspace_dlg_template: file location for the user input spreadsheet to write to
        :param ArchivalObject arch_obj: instance of ArchivalObject class containing data to be written to spreadsheet
        :param int row_number: running count of the row number to add data to

        """
        data_columns = {}
        # try:
        #     test = open(aspace_dlg_template, "r")  # TODO - add check to see if spreadsheet is open, if so, ask user to close spreadsheet
        # except OSError as open_error:
        #     logger.error(f'Could not open {aspace_dlg_template}: {open_error}\n')
        #     print(f'Could not open {aspace_dlg_template}, {open_error}\n'
        #           f'Make sure to close the spreadsheet before continuing')
        # else:
        temp_wb = load_workbook(aspace_dlg_template)
        for sheet in temp_wb:
            for row in sheet.iter_rows(max_row=1, max_col=28):
                for header in row:  # TODO - check if there are headers - don't want to write to blank sheet
                    data_columns[header.value] = utils.coordinate_to_tuple(header.coordinate)
            if "archival_object" not in data_columns:
                column_num = len(data_columns) + 1
                column_letter = utils.get_column_letter(column_num)
                cell_coordinate = f'{column_letter}1'
                sheet[cell_coordinate] = "Archival object URI"
                data_columns["Archival object URI"] = utils.coordinate_to_tuple(cell_coordinate)
            for column, coordinate in data_columns.items():
                if "DLG Collection ID" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.dlg_id
                elif "Box, Folder, and Item Number" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    bfi = [arch_obj.box, arch_obj.child, arch_obj.grandchild]
                    bfi_str = ""
                    for container in bfi:
                        if container:
                            bfi_str += container + ", "
                    sheet[cell_coordinate] = bfi_str[:-2]
                elif "record_id" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.record_id
                elif "dcterms_title" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.title
                elif "dcterms_creator" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.creator
                elif "dcterms_subject" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.subject
                elif "dcterms_description" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.description
                elif "dc_date" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.date
                elif "dcterms_spatial" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.subject_spatial
                elif "dcterms_medium" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.subject_medium
                elif "extent" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.extent
                elif "dcterms_language" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.language
                elif "dcterms_bibliographic_citation" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.citation
                elif "dlg_subject_personal" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.subject_personal
                elif "holding institution" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = "Hargrett Library"
                elif "public" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = "true"
                elif "archival_object" == column:
                    cell_letter = utils.get_column_letter(coordinate[1])
                    cell_coordinate = f'{cell_letter}{row_number}'
                    sheet[cell_coordinate] = arch_obj.arch_obj_uri
        temp_wb.save(aspace_dlg_template)
