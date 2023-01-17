import unittest
import as_export
from asnake.client import ASnakeClient
from as_export import *
from secrets import *


class MyTestCase(unittest.TestCase):
    def test_aspace_connection(self):
        local_aspace = as_export.ASpace(as_un, as_pw, as_api)
        connection_object = local_aspace.aspace_login()
        print(connection_object)
        self.assertIsInstance(connection_object, ASnakeClient)

    def test_grab_tcuri(self):
        local_aspace = as_export.ASpace(as_un, as_pw, as_api)
        connection_object = local_aspace.aspace_login()
        tc_uris = local_aspace.get_tcuri()
        self.assertTrue(tc_uris)  # return a non-empty list of results
    # test for grabbing archival objects get_archobjs


if __name__ == '__main__':
    unittest.main()
