import io
import unittest

from unittest import mock
from unittest.mock import patch, mock_open

from conjur.util.ssl_utils.errors import TLSSocketConnectionException
from conjur.errors import ConnectionToConjurFailedException
from conjur.logic.init_logic import InitLogic
from conjur.data_object.conjurrc_data import ConjurrcData
from conjur.util.ssl_utils import SSLClient

MOCK_CERT = '''
-----BEGIN CERTIFICATE-----
MIIDOD...
-----END CERTIFICATE-----
'''

EXPECTED_CONFIG = \
    '''---
    conjur_account: someaccount
    conjur_url: https://someurl
    cert_file: /path/to/conjur-someaccount.pem
    '''


class InitLogicTest(unittest.TestCase):
    conjurrc_data = ConjurrcData("my_url", "myorg", None)
    ssl_service = SSLClient
    capture_stream = io.StringIO()
    init_logic = InitLogic(ssl_service)

    '''
    Validates that certificate was written to the file
    '''

    @patch('builtins.input', return_value='yes')
    def test_certificate_is_written_to_file(self, mock_input):
        with patch("builtins.open", mock_open(read_data=MOCK_CERT)):
            is_written = self.init_logic.write_certificate_to_file(MOCK_CERT, "path/to/cert.pem",
                                                                   False)
            assert is_written is True
            assert open("path/to/cert").read() == MOCK_CERT

    '''
    Validates that when the user did not force the overwrite and the certificate 
    already exists that the certificate is not overwritten
    '''

    @patch('os.path.exists')
    def test_cert_exists_returns_not_written(self, mock_path_exists):
        mock_path_exists.return_value = True
        written = self.init_logic.write_certificate_to_file(MOCK_CERT, "/some/path/cert", False)
        self.assertEquals(written, False)

    '''
    Validates that when the user did not force the overwrite and the conjurrc already exists
    that the conjurrc is not written
    '''

    @patch('os.path.exists')
    def test_conjurrc_exists_returns_not_written(self, mock_path_exists):
        mock_path_exists.return_value = True
        written = self.init_logic.write_conjurrc(MOCK_CERT, "/some/path/cert", False)
        self.assertEquals(written, False)

    '''
    Validates that conjurrc was written to the file
    '''

    def test_conjurrc_is_written(self):
        with patch("builtins.open", mock_open(read_data=EXPECTED_CONFIG)):
            is_written = self.init_logic.write_conjurrc("path/to/conjurrc", self.conjurrc_data,
                                                        False)
            # assert that the file was written
            assert is_written is True
            assert open("path/to/conjurrc").read() == EXPECTED_CONFIG

    '''
    Validates that the conjurrc was written in the proper format
    '''

    def test_conjurrc_is_written_formatted_correctly(self):
        with mock.patch.object(self.init_logic, '_InitLogic__overwrite_file_if_exists', create=True,
                               return_value=None):
            with patch("builtins.open", mock_open(read_data=EXPECTED_CONFIG)):
                self.init_logic.write_conjurrc("path/to/conjurrc", self.conjurrc_data, False)
                with open('path/to/conjurrc', 'r') as conjurrc:
                    lines = conjurrc.readlines()
                    self.assertEquals(lines[0].strip(), "---")
                    self.assertEquals(lines[1].strip(), "conjur_account: someaccount")
                    self.assertEquals(lines[3].strip(),
                                      "cert_file: /path/to/conjur-someaccount.pem")

    '''
    Validates that Conjur can connect to server
    '''

    def test_dns_error_will_raise_exception(self):
        with patch.object(SSLClient, 'get_certificate',
                          side_effect=TLSSocketConnectionException("err")) as mock_get_cert:
            with self.assertRaises(ConnectionToConjurFailedException) as context:
                init_logic = InitLogic(self.ssl_service())
                init_logic.get_certificate('https://url', None)
            self.assertRegex(str(context.exception), 'Unable to resolve server DNS ')

    def test_timeout_error_will_raise_exception(self):
        with patch.object(SSLClient, 'get_certificate', side_effect=TimeoutError) as mock_get_cert:
            with self.assertRaises(ConnectionToConjurFailedException) as context:
                init_logic = InitLogic(self.ssl_service)
                init_logic.get_certificate('https://url', None)
            self.assertRegex(str(context.exception), 'Unable to connect to server ')

    def test_cert_error_will_raise_exception(self):
        with patch.object(SSLClient, 'get_certificate', side_effect=Exception) as mock_get_cert:
            with self.assertRaises(Exception) as context:
                init_logic = InitLogic(self.ssl_service)
                init_logic.get_certificate('https://url', None)
            self.assertRegex(str(context.exception), 'Unable to retrieve certificate from ')

    '''
    Validates that the fingerprint and certificate that were returned 
    from the inner called service are also returned by the caller
    '''

    def test_fingerprint_and_certificate_are_properly_returned(self):
        with patch.object(SSLClient, 'get_certificate', return_value=["12:AB", "cert"]) as mock_ssl:
            mock_init_command = InitLogic(self.ssl_service)
            fingerprint, readable_certificate = mock_init_command.get_certificate("https://someurl",
                                                                                  443)
            self.assertEquals(fingerprint, "12:AB")
            self.assertEquals(readable_certificate, "cert")
