import unittest

from conjur.init.conjurrc_data import ConjurrcData

EXPECTED_REP_OBJECT={'appliance_url': 'https://someurl', 'account': 'someaccount', 'cert_file': None, 'plugins': []}

class InitCommandLogicTest(unittest.TestCase):

    def test_conjurrc_object_representation(self):
        conjurrc_data = ConjurrcData("https://someurl", "someaccount", None)
        rep_obj = conjurrc_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)
