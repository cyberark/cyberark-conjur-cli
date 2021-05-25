import unittest
from unittest.mock import mock_open, patch

from conjur.data_object.conjurrc_data import ConjurrcData
from conjur.errors import InvalidConfigurationException

EXPECTED_REP_OBJECT={'conjur_url': 'https://someurl', 'conjur_account': 'someaccount', 'cert_file': "/some/cert/path"}
EXPECTED_CONJURRC = \
"""
---
conjur_account: someacc
conjur_url: https://someurl
cert_file: /some/path/to/pem
"""

CONJURRC_DICT = {'conjur_url': 'https://someurl', 'conjur_account': 'someacc', 'cert_file': '/some/path/to/pem'}

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

    @patch('builtins.open', side_effect=KeyError)
    def test_conjurrc_throws_error_when_key_is_missing(self, mock_open):
        mock_conjurrc = ConjurrcData("https://someurl", "someaccount", "/some/cert/path")
        with self.assertRaises(InvalidConfigurationException):
            mock_conjurrc.load_from_file()