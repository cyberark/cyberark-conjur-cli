import io
import unittest

from contextlib import redirect_stdout
from unittest import mock
from unittest.mock import patch, mock_open

from conjur.init.init_logic import InitLogic
from conjur.init.conjurrc_data import ConjurrcData
from conjur.ssl_service import SSLService

MOCK_CERT='''
-----BEGIN CERTIFICATE-----
MIIDOD...
-----END CERTIFICATE-----
'''

EXPECTED_CONFIG= \
'''---
account: someaccount
appliance_url: https://someurl
cert_file: /path/to/conjur-someaccount.pem
plugins: [foo, bar]
'''

class InitLogicTest(unittest.TestCase):
    conjurrc_data = ConjurrcData("my_url", "myorg", None)
    ssl_service = SSLService
    capture_stream = io.StringIO()
    init_logic = InitLogic(ssl_service)

    '''
    Validates that certificate was written to the file
    '''
    @patch('builtins.input', return_value='yes')
    def test_certificate_is_written_to_file(self, mock_input):
        with mock.patch.object(self.init_logic, '_InitLogic__overwrite_file_if_exists', create=True, return_value=None):
            with patch("builtins.open", mock_open(read_data=MOCK_CERT)) as mock_file:
                with redirect_stdout(self.capture_stream):
                    self.init_logic.write_certificate_to_file(MOCK_CERT, "path/to/cert.pem", False)

                    assert open("path/to/cert").read() == MOCK_CERT
                    self.assertEquals(self.capture_stream.getvalue().strip(), "Wrote certificate to path/to/cert.pem")

    '''
    Validates that conjurrc was written to the file
    '''
    def test_conjurrc_is_written(self):
        with mock.patch.object(self.init_logic, '_InitLogic__overwrite_file_if_exists', create=True, return_value=None):
            with patch("builtins.open", mock_open(read_data=EXPECTED_CONFIG)):
                with redirect_stdout(self.capture_stream):
                    self.init_logic.write_conjurrc("path/to/conjurrc", self.conjurrc_data, False)

                    assert open("path/to/conjurrc").read() == EXPECTED_CONFIG
                    self.assertRegex(self.capture_stream.getvalue().strip(), "Wrote configuration to path/to/conjurrc")

    @patch('builtins.input', return_value='no')
    @mock.patch('os.path.isfile')
    def test_user_does_not_want_to_overwrite_raises_exception(self, mock_path, mock_input):
        mock_path.return_value = True
        with self.assertRaises(Exception):
            self.init_logic._overwrite_file_if_exists("somefile", False)

    '''
    Validates that the conjurrc was written in the proper format
    '''
    def test_conjurrc_is_written_formatted_correctly(self):
        with mock.patch.object(self.init_logic, '_InitLogic__overwrite_file_if_exists', create=True, return_value=None):
            with patch("builtins.open", mock_open(read_data=EXPECTED_CONFIG)):
                self.init_logic.write_conjurrc("path/to/conjurrc", self.conjurrc_data, False)
                with open('path/to/conjurrc', 'r') as conjurrc:
                    lines = conjurrc.readlines()
                    assert lines[0].strip() == "---"
                    assert lines[1].strip() == "account: someaccount"
                    assert lines[3].strip() == "cert_file: /path/to/conjur-someaccount.pem"
                    assert lines[4].strip() == "plugins: [foo, bar]"

    def test_cert_error_will_raise_exception(self):
        with patch.object(SSLService, 'get_certificate', side_effect=Exception) as mock_get_cert:
            with self.assertRaises(Exception) as context:
                init_logic = InitLogic(self.ssl_service)
                init_logic.get_certificate('https://url', None)

            self.assertRegex(str(context.exception), 'Unable to retrieve certificate from')

    '''
    Validates that the fingerprint and certificate that were returned 
    from the inner called service are also returned by the caller
    '''
    def test_fingerprint_and_certificate_are_properly_returned(self):
        with patch.object(SSLService, 'get_certificate', return_value=["12:AB", "cert"]) as mock_ssl:
            mock_init_command = InitLogic(self.ssl_service)
            fingerprint, readable_certificate = mock_init_command.get_certificate("https://someurl", 443)

            self.assertEquals(fingerprint, "12:AB")
            self.assertEquals(readable_certificate, "cert")
