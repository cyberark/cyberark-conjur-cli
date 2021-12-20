import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch, MagicMock

import OpenSSL
from OpenSSL import SSL

from conjur.api.models import SslVerificationMetadata, SslVerificationMode
from conjur.constants import TEST_HOSTNAME
from conjur.errors import CertificateHostnameMismatchException, InvalidURLFormatException, \
    CertificateNotTrustedException, MissingRequiredParameterException, HttpSslError, HttpStatusError
from conjur.logic.init_logic import InitLogic as InitLogic
from conjur.controller.init_controller import InitController as InitController
from conjur.data_object.conjurrc_data import ConjurrcData
from conjur.api.ssl_utils.ssl_client import SSLClient

MockConjurrcData = ConjurrcData(conjur_url=TEST_HOSTNAME, account="admin")


class MOCK_FORMATTED_URL:
    hostname = MockConjurrcData.conjur_url
    port = 443
    scheme = "somescheme"


class InitControllerTest(unittest.TestCase):
    capture_stream = io.StringIO()
    conjurrc_data = ConjurrcData()
    ssl_service = SSLClient
    init_logic = InitLogic(ssl_service)
    force_overwrite = False
    ssl_verification_metadata = SslVerificationMetadata(SslVerificationMode.WITH_TRUST_STORE)

    def test_init_constructor(self):
        mock_conjurrc_data = None
        mock_init_logic = None
        mock_force = False
        mock_ssl_verification_data = SslVerificationMetadata(SslVerificationMode.NO_SSL)
        InitController(mock_conjurrc_data, mock_init_logic, mock_force, mock_ssl_verification_data)
        assert InitController.conjurrc_data == mock_conjurrc_data
        assert InitController.init_logic == mock_init_logic
        assert InitController.force_overwrite == mock_force

    '''
    When user does not supply an account a Runtime error should be raised
    '''

    @patch('builtins.input', return_value='')
    @patch('conjur.logic.init_logic')
    def test_init_without_host_raises_error(self, mock_init_logic, mock_input):
        mock_init_logic.fetch_account_from_server = MagicMock(side_effect=HttpStatusError(status=401))
        mock_conjurrc_data = ConjurrcData()
        with self.assertRaises(MissingRequiredParameterException):
            mock_conjurrc_data.conjur_url = 'https://someurl'
            mock_init_controller = InitController(mock_conjurrc_data, mock_init_logic, False,
                                                  self.ssl_verification_metadata)
            mock_init_controller._get_account_info_if_not_exist()

    @patch('builtins.input', return_value='someaccount')
    @patch('conjur.logic.init_logic')
    def test_init_host_is_added_to_conjurrc_object(self, mock_init_logic, mock_input):
        mock_init_logic.fetch_account_from_server = MagicMock(side_effect=HttpStatusError(status=401))
        mock_conjurrc_data = ConjurrcData()
        mock_conjurrc_data.conjur_url = "https://someaccount"
        mock_init_controller = InitController(mock_conjurrc_data, mock_init_logic, False,
                                              self.ssl_verification_metadata)
        mock_init_controller._get_account_info_if_not_exist()
        self.assertEquals(mock_conjurrc_data.conjur_account, 'someaccount')

    '''
    When user does not trust the certificate, an exception will be raised
    '''

    @patch('builtins.input', side_effect=['no'])
    def test_init_not_trusting_cert_raises_error(self, mock_input):
        self.conjurrc_data.conjur_url = 'https://someurl'
        ctx = SSL.Context(method=SSL.TLSv1_2_METHOD)
        sock = OpenSSL.SSL.Connection(ctx)
        self.init_logic.connect = MagicMock(return_value=sock)
        self.init_logic.get_certificate = MagicMock(return_value=["12:AB", "somecertchain"])

        with self.assertRaises(CertificateNotTrustedException):
            init_controller = InitController(self.conjurrc_data, self.init_logic, self.force_overwrite,
                                             self.ssl_verification_metadata)
            init_controller._get_server_certificate(MOCK_FORMATTED_URL)

    '''
    When user trusts the certificate, the certificate should be returned
    '''

    @patch('builtins.input', side_effect=['yes'])
    def test_init_user_trusts_cert_returns_cert(self, mock_input):
        mock_certificate = "cert"
        self.conjurrc_data.conjur_url = "https://someurl"
        self.init_logic.get_certificate = MagicMock(return_value=["12:AB", mock_certificate])
        init_controller = InitController(self.conjurrc_data, self.init_logic, self.force_overwrite,
                                         self.ssl_verification_metadata)
        fetched_certificate = init_controller._get_server_certificate(MOCK_FORMATTED_URL)
        self.assertEquals(fetched_certificate, mock_certificate)

    @patch('builtins.input', side_effect=['http://someurl'])
    def test_user_supplied_certificate_returns_none(self, mock_input):
        cert_file = "/some/path/somepem.pem"
        self.conjurrc_data.cert_file = cert_file
        ssl_verification_data = SslVerificationMetadata(SslVerificationMode.WITH_CA_BUNDLE, cert_file)
        init_controller = InitController(self.conjurrc_data, self.init_logic, self.force_overwrite,
                                         ssl_verification_data)
        fetched_certificate = init_controller._get_server_certificate(MOCK_FORMATTED_URL)
        assert self.conjurrc_data.cert_file == "/some/path/somepem.pem"
        self.assertEquals(fetched_certificate, None)

    @patch('conjur.logic.init_logic')
    def test_user_supplies_cert_writes_to_file_not_called(self, mock_init_logic):
        InitController._write_certificate(self, "https://some/cert/path")
        mock_init_logic.write_certificate_to_file.assert_not_called()

    '''
    Validates that when the user wants to overwrite the certificate file,
    We attempt to write the certificate twice (initial attempt 
    and user after confirmation)
    '''

    # The certificate file exists and the CLI prompts
    # if the user wants to overwrite
    @patch('conjur.logic.init_logic')
    @patch('builtins.input', return_value='yes')
    def test_user_confirms_force_overwrites_writes_cert_to_file(self, mock_input, mock_init_logic):
        with redirect_stdout(self.capture_stream):
            self.conjurrc_data.conjur_url = "https://someurl"
            init_controller = InitController(self.conjurrc_data, mock_init_logic, False, self.ssl_verification_metadata)
            # Mock that a certificate file already exists
            mock_init_logic.write_certificate_to_file.return_value = False
            init_controller._write_certificate('some_cert')

        self.assertRegex(self.capture_stream.getvalue(), "Certificate written to")
        mock_init_logic.write_certificate_to_file.assert_called_with('some_cert', '/root/conjur-server.pem', True)
        self.assertEquals(mock_init_logic.write_certificate_to_file.call_count, 2)

    '''
    Validates that when the user wants to overwrite the conjurrc file,
    We attempt to write the conjurrc twice (initial attempt 
    and user after confirmation)
    '''

    # The conjurrc file exists and the CLI prompts
    # if the user wants to overwrite
    @patch('conjur.logic.init_logic')
    @patch('builtins.input', return_value='yes')
    def test_user_confirms_force_overwrites_writes_conjurrc_to_file(self, mock_input, mock_init_logic):
        with redirect_stdout(self.capture_stream):
            self.conjurrc_data.conjur_url = "https://someurl"
            init_controller = InitController(self.conjurrc_data, mock_init_logic, False, self.ssl_verification_metadata)
            # Mock that a conjurrc file already exists
            mock_init_logic.write_conjurrc.return_value = False
            init_controller.write_conjurrc()
            self.assertRegex(self.capture_stream.getvalue(), "Configuration written to")
            mock_init_logic.write_conjurrc.assert_called_with('/root/.conjurrc', self.conjurrc_data, True)
            self.assertEquals(mock_init_logic.write_conjurrc.call_count, 2)

    @patch('builtins.input', return_value='')
    def test_user_does_not_input_url_raises_error(self, mock_input):
        mock_conjurrc_data = ConjurrcData(conjur_url=None)
        with self.assertRaises(InvalidURLFormatException) as context:
            init_controller = InitController(mock_conjurrc_data, self.init_logic, self.force_overwrite,
                                             self.ssl_verification_metadata)
            init_controller._prompt_for_conjur_url()
        self.assertRegex(str(context.exception), 'Error: URL is required')

    @patch('builtins.input', return_value=MockConjurrcData.conjur_url)
    def test_user_does_not_input_https_will_raises_error(self, mock_input):
        mock_conjurrc_data = ConjurrcData(conjur_url='somehost')
        with self.assertRaises(InvalidURLFormatException) as context:
            init_controller = InitController(mock_conjurrc_data, self.init_logic, self.force_overwrite,
                                             self.ssl_verification_metadata)
            init_controller._validate_conjur_url(MOCK_FORMATTED_URL)
        self.assertRegex(str(context.exception), 'Error: undefined behavior')

    @patch('builtins.input', return_value='no')
    def test_user_does_not_overwrite_raises_error(self, mock_input):
        init_controller = InitController(ConjurrcData, InitLogic, False, self.ssl_verification_metadata)
        with self.assertRaises(Exception):
            init_controller.ensure_overwrite_file('someconfig')

    @patch('conjur.logic.init_logic')
    def test_user_raises_certificate_hostname_mismatch_error(self, mock_init_logic):
        mock_init_logic.fetch_account_from_server = MagicMock(side_effect=CertificateHostnameMismatchException)
        init_controller = InitController(ConjurrcData(account=None), mock_init_logic, False,
                                         self.ssl_verification_metadata)
        with self.assertRaises(CertificateHostnameMismatchException):
            init_controller._get_account_info_if_not_exist()
