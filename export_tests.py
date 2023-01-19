import unittest
import as_export
from asnake.client import ASnakeClient
from as_export import *
from secrets import *


class TestASpaceFunctions(unittest.TestCase):
    local_aspace = as_export.ASpace(as_un, as_pw, as_api)

    def test_aspace_connection(self):
        self.local_aspace.aspace_login()
        self.assertIsInstance(self.local_aspace.client, ASnakeClient)

    def test_grab_tcuri(self):
        tc_uris = self.local_aspace.get_tcuri()
        self.assertTrue(tc_uris)  # return a non-empty list of results

    def test_test_api(self):
        test_message = self.local_aspace.test_api()
        self.assertIsInstance(test_message, str)

    def test_get_repos(self):
        test_repositories = self.local_aspace.get_repos()
        self.assertTrue(test_repositories)

    # test for grabbing archival objects get_archobjs


if __name__ == '__main__':
    unittest.main()
