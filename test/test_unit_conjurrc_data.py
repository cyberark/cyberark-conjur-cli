import unittest
from unittest.mock import mock_open, patch

from conjur.data_object import ConjurrcData, AuthnTypes
from conjur.errors import InvalidConfigurationException

class ConjurrcDataTest(unittest.TestCase):

    def test_conjurrc_object_representation(self):
        conjurrc_data = ConjurrcData("https://someurl", "someaccount", "/some/cert/path")
        rep_obj = conjurrc_data.__repr__()
        expected_rep_obj = {'conjur_url': 'https://someurl', 'conjur_account': 'someaccount', 'cert_file': "/some/cert/path", 'authn_type': AuthnTypes.AUTHN, 'service_id': None, 'netrc_path' : None}
        self.assertEquals(str(expected_rep_obj), rep_obj)

    def test_conjurrc_object_is_filled_correctly(self):
        read_data = \
"""
---
account: someacc
appliance_url: https://someurl
cert_file: /some/path/to/pem
netrc_path: /some/path/to/netrc
"""
        expected_dict = {'conjur_url': 'https://someurl', 'conjur_account': 'someacc', 'cert_file': '/some/path/to/pem', 'authn_type': AuthnTypes.AUTHN, 'service_id': None, 'netrc_path' : '/some/path/to/netrc'}
        with patch("builtins.open", mock_open(read_data=read_data)):
            mock_conjurrc_data = ConjurrcData.load_from_file()
            self.assertEquals(mock_conjurrc_data.__dict__, expected_dict)

    def test_conjurrc_accepts_alternative_keynames(self):
        read_data = \
"""
---
conjur_account: someacc
conjur_url: https://someurl
cert_file: /some/path/to/pem
"""
        expected_dict = {'conjur_url': 'https://someurl', 'conjur_account': 'someacc', 'cert_file': '/some/path/to/pem', 'authn_type': AuthnTypes.AUTHN, 'service_id': None, 'netrc_path' : None}
        with patch("builtins.open", mock_open(read_data=read_data)):
            mock_conjurrc_data = ConjurrcData.load_from_file()
            self.assertEquals(mock_conjurrc_data.__dict__, expected_dict)

    @patch('builtins.open', side_effect=KeyError)
    def test_conjurrc_throws_error_when_key_is_missing(self, mock_open):
        mock_conjurrc = ConjurrcData("https://someurl", "someaccount", "/some/cert/path")
        with self.assertRaises(InvalidConfigurationException):
            mock_conjurrc.load_from_file()

    def test_conjurrc_throws_error_when_invalid_authn_type(self):
        read_data = \
"""
---
account: someacc
appliance_url: https://someurl
cert_file: /some/path/to/pem
authn_type: abcd
"""
        with patch("builtins.open", mock_open(read_data=read_data)):
            with self.assertRaises(InvalidConfigurationException) as context:
                ConjurrcData.load_from_file()
            self.assertRegex(str(context.exception), "Invalid authn_type")
