import unittest
import aspace
from asnake.client import ASnakeClient

import gui
from aspace import *
from gui import *
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
        error, tc_uris = self.local_aspace.get_tcuri(barcode, repository)
        self.assertTrue(tc_uris)  # return a non-empty list of results
        self.assertIsInstance(error, bool)  # return True or False if error was caught searching tc uris

    def test_getarchobjs(self):
        pass

    def test_get_repos(self):
        test_repositories = self.local_aspace.get_repos()
        self.assertTrue(test_repositories)

    archival_object = ""

    def test_parse_archivalobject(self):
        pass

    def test_resourceinfo(self):
        pass

    # test for grabbing archival objects get_archobjs


class TestGUIFunctions(unittest.TestCase):

    def test_aspace_login(self):
        test_defaults = {"as_api": ""}
        close, as_instance, repos = gui.get_aspace_login(test_defaults)
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

    def test_get_barcodes(self):
        pass

    def test_write_template(self):
        pass


if __name__ == '__main__':
    unittest.main()
