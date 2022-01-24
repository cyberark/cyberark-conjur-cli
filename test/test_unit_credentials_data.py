import unittest

from conjur_api.models import CredentialsData

EXPECTED_REP_OBJECT = {'machine': 'https://someurl', 'username': 'someid', 'password': "****"}


class CredentialsDataTest(unittest.TestCase):

    def test_credentials_data_object_representation(self):
        credentals_data = CredentialsData("https://someurl", "someid", "somepass")
        rep_obj = credentals_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)
