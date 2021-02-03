import unittest

from conjur.data_objects.conjurrc_data import ConjurrcData

EXPECTED_REP_OBJECT={'appliance_url': 'https://someurl', 'account': 'someaccount', 'cert_file': "/some/cert/path", 'plugins': []}

class ConjurrcDataTest(unittest.TestCase):

    def test_conjurrc_object_representation(self):
        conjurrc_data = ConjurrcData("https://someurl", "someaccount", "/some/cert/path")
        rep_obj = conjurrc_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)
