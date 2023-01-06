import unittest
import as_export
from as_export import *
from secrets import *


class MyTestCase(unittest.TestCase):
    def test_aspace_connection(self):
        aspace_connection = as_export.ASpace(as_un, as_pw, as_api)
        connection_status = aspace_connection.aspace_login()
        print(connection_status)
        self.assertEqual(connection_status, 200)  # need to change this to receive just some status, could be incorrect

    # test for grabbing archival objects get_archobjs


if __name__ == '__main__':
    unittest.main()
