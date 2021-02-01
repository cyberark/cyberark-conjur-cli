import netrc
import unittest
from unittest.mock import MagicMock, patch, mock_open

from conjur.credentials_from_file import CredentialsFromFile


class MockCredentialsData:
    machine = 'https://someurl/authn'
    login = 'somelogin'
    api_key = 'somepass'


class MockNetrc:
    hosts = {'https://someurl/authn': ('somelogin', None, 'somepass')}
    machine = 'https://someurl/authn'
    login = 'somelogin'
    password = 'somepass'


class MockEmptyNetrc:
    hosts = {}
    machine = ''
    login = ''
    password = ''


EXPECTED_NETRC = \
    '''machine https://someurl/authn
login somelogin
password somepass
'''

class CredentialsFromFileTest(unittest.TestCase):

    @patch('os.path.exists', return_value=True)
    @patch('os.chmod')
    def test_credentials_load_calls_build_netrc(self, mock_exists, mock_chmod):
        netrc.netrc = MagicMock(return_value=MockNetrc)
        credentials = CredentialsFromFile()
        credentials.build_netrc = MagicMock()
        credentials.save(MockCredentialsData)
        credentials.build_netrc.assert_called_once_with(MockNetrc)

    @patch('os.path.exists', return_value=False)
    @patch('os.chmod')
    def test_credentials_load_writes_new_netrc_entry_if_file_does_not_exist(self, mock_does_not_exist, mock_chmod):
        with patch("builtins.open", mock_open(read_data=EXPECTED_NETRC)):
            credentials = CredentialsFromFile()
            credentials.save(MockCredentialsData)
            with open('path/to/netrc', 'r') as netrc:
                lines = netrc.readlines()
                assert lines[0].strip() == "machine https://someurl/authn"
                assert lines[1].strip() == "login somelogin"
                assert lines[2].strip() == "password somepass"

    def test_credentials_netrc_exists_but_is_empty_raises_exception(self):
        netrc.netrc = MagicMock(return_value=MockEmptyNetrc)
        with self.assertRaises(Exception):
            credentials = CredentialsFromFile()
            credentials.load("https://someurl")

    def test_loaded_credentials_returns_proper_dict(self):
        netrc.netrc = MagicMock(return_value=MockNetrc)
        netrc.netrc.hosts = MagicMock()
        netrc.netrc.return_value.authenticators = MagicMock(return_value=('somelogin', None, 'somepass'))
        credentials = CredentialsFromFile()
        assert credentials.load("https://someurl") == {'machine': 'https://someurl/authn',
                                                       'api_key': 'somepass',
                                                       'login_id': 'somelogin'}

    def test_credentials_netrc_exists_but_no_entry_is_found_raises_exception(self):
        with self.assertRaises(Exception):
            with patch('netrc.netrc'):
                credentials = CredentialsFromFile()
                credentials.load("https://someurl")

    def test_build_netrc_writes_to_file_correctly(self):
        with patch("builtins.open", mock_open(read_data=EXPECTED_NETRC)):
            credentials = CredentialsFromFile()
            credentials.build_netrc(MockCredentialsData)
            with open('path/to/netrc', 'r') as netrc:
                lines = netrc.readlines()
                assert lines[0].strip() == "machine https://someurl/authn"
                assert lines[1].strip() == "login somelogin"
                assert lines[2].strip() == "password somepass"
