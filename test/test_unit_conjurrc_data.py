import unittest
from unittest.mock import mock_open, patch

from conjur.init.conjurrc_data import ConjurrcData

EXPECTED_REP_OBJECT={'appliance_url': 'https://someurl', 'account': 'someaccount', 'cert_file': "/some/cert/path", 'plugins': []}
EXPECTED_CONJURRC = \
"""
---
account: someacc
appliance_url: https://someurl
cert_file: /some/path/to/pem
plugins: []
"""

CONJURRC_DICT = {'appliance_url': 'https://someurl', 'account': 'someacc', 'cert_file': '/some/path/to/pem', 'plugins':[]}

class ConjurrcDataTest(unittest.TestCase):

    def test_conjurrc_object_representation(self):
        conjurrc_data = ConjurrcData("https://someurl", "someaccount", "/some/cert/path")
        rep_obj = conjurrc_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)

    @patch('yaml.load', return_value=CONJURRC_DICT)
    def test_conjurrc_object_is_filled_correctly(self, mock_yaml_load):
         with patch("builtins.open", mock_open(read_data=EXPECTED_CONJURRC)):
            mock_conjurrc_data = ConjurrcData.load_from_file()
            self.assertEquals(mock_conjurrc_data.__dict__, CONJURRC_DICT)
