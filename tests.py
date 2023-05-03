import unittest

from aspace import *
from gui import *
from spreadsheet import *
from secrets import *


class TestASpaceFunctions(unittest.TestCase):
    local_aspace = aspace.ASpace(as_un, as_pw, as_api)

    def test_test_api(self):
        test_message = self.local_aspace.test_api()
        self.assertIsInstance(test_message, str)

    def test_aspace_connection(self):
        self.local_aspace.aspace_login()
        self.assertIsInstance(self.local_aspace.client, ASnakeClient)

    def test_grab_tcuri(self):
        barcode = 32108050893687  # use these for unittests
        repository = 4  # use these for unittests
        self.local_aspace.aspace_login()
        error, tc_uris = self.local_aspace.get_tcuri(barcode, repository)
        self.assertTrue(tc_uris)  # return a non-empty list of results
        if error:
            self.assertIsInstance(error, bool)  # return True or False if error was caught searching tc uris

    def test_getarchobjs(self):
        barcode = 32108050893687  # use these for unittests
        repository = 4  # use these for unittests
        results, error = self.local_aspace.get_archobjs(barcode, repository)
        self.assertTrue(results)  # return a non-empty list of results
        if error:
            self.assertIsInstance(error, bool)
        pass

    def test_get_repos(self):
        test_repositories = self.local_aspace.get_repos()
        self.assertTrue(test_repositories)

    def test_parse_archobj(self):
        archobj_example = Path(os.getcwd(), "test_data/archival_object.json")
        with open(archobj_example, "r", encoding='utf-8') as archobj_data:
            resource_obj = aspace.ResourceObject()
            test_data = json.loads(archobj_data.read())
            resource_obj.uri = "/repositories/4/resources/3155"  # set this to prevent getting resource info
            archobj_inst = ArchivalObject(test_data, "guan_1234a")
            archobj_inst.parse_archobj(self.local_aspace.client, resource_obj)
        self.assertEqual(archobj_inst.title, "Blackwell, Louise and Clay, Frances - Florida State University regarding "
                                             "a critical study of Smith's work")
        self.assertEqual(archobj_inst.box, "box 1")
        self.assertEqual(archobj_inst.child, "folder 23")

    def test_get_resource_info(self):
        archobj_example = Path(os.getcwd(), "test_data/resource.json")
        with open(archobj_example, "r", encoding='utf-8') as resource_data:
            test_data = json.loads(resource_data.read())
            resource_ex = aspace.ResourceObject(test_data)
            resource_ex.get_resource_info(self.local_aspace.client)
            self.assertEqual(resource_ex.language, "eng")
            self.assertEqual(resource_ex.subjper, "Snelling, Paula||Smith, Esther")
            self.assertEqual(resource_ex.citation, "Lillian Eugenia Smith papers, ms1283a. Hargrett Rare Book and "
                                                   "Manuscript Library, The University of Georgia Libraries.")

    # test for grabbing archival objects get_archobjs


class TestGUIFunctions(unittest.TestCase):

    def test_aspace_login(self):
        test_defaults = {"as_api": ""}
        close, as_instance, repos = get_aspace_login(test_defaults)
        self.assertIsInstance(as_instance, ASpace)
        self.assertIsInstance(close, bool)
        self.assertIsInstance(repos, dict)
        self.assertTrue(repos, dict)  # make sure repos has repos in it

    def test_delete_logfiles(self):
        current_directory = os.getcwd()
        logs_path = Path(current_directory, "logs")
        for file in os.listdir(logs_path):
            logfile = Path(logs_path, file)
            file_time = os.path.getmtime(logfile)
            current_time = time.time()
            delete_time = current_time - 2630000  # This is for 1 month.
            self.assertGreaterEqual(file_time, delete_time)


class TestSpreadsheetFunctions(unittest.TestCase):

    def test_sort_input(self):
        test_input = "32108050893687,32108051113895,32108050892861"
        sorted_results = Spreadsheet.sort_input(test_input)
        self.assertGreaterEqual(len(sorted_results), 0)
        self.assertEqual(type(sorted_results[0]), str)

    def test_get_cell_coordinate(self):
        coordinate = (1,1)
        row_num = 2
        test_cell_coord = Spreadsheet.get_cell_coordinate(coordinate, row_num)
        self.assertEqual(test_cell_coord, "A2")

    def test_write_template(self):
        pass


if __name__ == '__main__':
    unittest.main()
