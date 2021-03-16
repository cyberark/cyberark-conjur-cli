import netrc
import unittest
from unittest.mock import MagicMock, patch, mock_open

from conjur.data_object import CredentialsData
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from test.util import test_helpers as utils

class MockCredentialsData:
    machine = 'https://someurl'
    login = 'somelogin'
    password = 'somepass'


class MockNetrc:
    hosts = {'https://someurl': ('somelogin', None, 'somepass')}
    machine = 'https://someurl'
    login = 'somelogin'
    password = 'somepass'


class MockEmptyNetrc:
    hosts = {}
    machine = ''
    login = ''
    password = ''


EXPECTED_NETRC = \
    '''machine https://someurl
login somelogin
password somepass
'''

class FileCredentialsProviderTest(unittest.TestCase):
    @patch('os.path.exists', return_value=True)
    @patch('os.chmod')
    def test_credentials_load_calls_build_netrc(self, mock_exists, mock_chmod):
        netrc.netrc = MagicMock(return_value=MockNetrc)
        credentials = FileCredentialsProvider()
        credentials.build_netrc = MagicMock()
        credentials.save(MockCredentialsData)
        credentials.build_netrc.assert_called_once_with(MockNetrc)

    @patch('os.path.exists', return_value=False)
    @patch('os.chmod')
    def test_credentials_load_writes_new_netrc_entry_if_file_does_not_exist(self, mock_does_not_exist, mock_chmod):
        with patch("builtins.open", mock_open(read_data=EXPECTED_NETRC)):
            credentials = FileCredentialsProvider()
            credentials.save(MockCredentialsData)
            utils.validate_netrc_contents(self)

    def test_credentials_netrc_exists_but_is_empty_raises_exception(self):
        netrc.netrc = MagicMock(return_value=MockEmptyNetrc)
        with self.assertRaises(Exception):
            credentials = FileCredentialsProvider()
            credentials.load("https://someurl")

    def test_loaded_credentials_returns_proper_object(self):
        netrc.netrc = MagicMock(return_value=MockNetrc)
        netrc.netrc.hosts = MagicMock()
        netrc.netrc.return_value.authenticators = MagicMock(return_value=('somelogin', None, 'somepass'))
        with patch.object(FileCredentialsProvider, 'is_exists', return_value=True):
            credentials = FileCredentialsProvider()
            self.assertEquals(credentials.load("https://someurl"), CredentialsData(machine='https://someurl', password='somepass', login='somelogin'))

    def test_credentials_netrc_exists_but_no_entry_is_found_raises_exception(self):
        with self.assertRaises(Exception):
            with patch('netrc.netrc'):
                credentials = FileCredentialsProvider()
                credentials.load("https://someurl")

    def test_build_netrc_writes_to_file_correctly(self):
        with patch("builtins.open", mock_open(read_data=EXPECTED_NETRC)):
            credentials = FileCredentialsProvider()
            credentials.build_netrc(MockCredentialsData)
            utils.validate_netrc_contents(self)
