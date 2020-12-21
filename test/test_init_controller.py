import io
import unittest
from unittest.mock import patch, MagicMock

import OpenSSL
from OpenSSL import SSL

from conjur.init.init_logic import InitLogic as InitLogic
from conjur.init.init_controller import InitController as InitController
from conjur.init.conjurrc_data import ConjurrcData
from conjur.ssl_service import SSLService

class InitControllerTest(unittest.TestCase):
    capture_stream = io.StringIO()
    conjurrc_data = ConjurrcData()
    ssl_service = SSLService
    init_logic = InitLogic(ssl_service)
    force_overwrite = False

    def test_init_constructor(self):
        mock_conjurrc_data = None
        mock_init_logic = None
        mock_force = False
        InitController(mock_conjurrc_data, mock_init_logic, mock_force)

        assert InitController.conjurrc_data == mock_conjurrc_data
        assert InitController.init_logic == mock_init_logic
        assert InitController.force_overwrite == mock_force

    '''
    When user does not supply an account a Runtime error should be raised
    '''
    @patch('builtins.input', return_value=None)
    def test_init_without_host_raises_error(self, mock_input):
        self.conjurrc_data.account=None
        with self.assertRaises(RuntimeError):
            self.conjurrc_data.appliance_url = 'https://someurl'
            InitController.get_account_info(self, self.conjurrc_data, "cert")

    @patch('builtins.input', return_value='someaccount')
    def test_init_host_is_added_to_conjurrc_object(self, mock_input):
        InitController.get_account_info(self, self.conjurrc_data, "cert")
        self.assertEquals(self.conjurrc_data.account, 'someaccount')

    '''
    When user does not trust the certificate, an exception will be raised
    '''
    @patch('builtins.input', side_effect=['no'])
    def test_init_not_trusting_cert_raises_error(self, mock_input):
        self.conjurrc_data.appliance_url = 'https://someurl'

        ctx = SSL.Context(method=SSL.TLSv1_2_METHOD)
        sock = OpenSSL.SSL.Connection(ctx)
        self.init_logic.connect = MagicMock(return_value = sock)
        self.init_logic.get_certificate = MagicMock(return_value = ["12:AB", "somecertchain"])

        with self.assertRaises(ValueError):
            init_controller = InitController(self.conjurrc_data,self.init_logic, self.force_overwrite)
            init_controller.get_server_certificate()

    '''
    When user trusts the certificate, the certificate should be returned
    '''
    @patch('builtins.input', side_effect=['yes'])
    def test_init_user_trusts_cert_returns_cert(self, mock_input):
        mock_certificate = "cert"
        self.conjurrc_data.appliance_url = "https://someurl"
        self.init_logic.get_certificate = MagicMock(return_value = ["12:AB", mock_certificate])
        init_controller = InitController(self.conjurrc_data,self.init_logic, self.force_overwrite)
        fetched_certificate = init_controller.get_server_certificate()
        self.assertEquals(fetched_certificate, mock_certificate)

    '''
    When URL scheme is HTTP, no certificate should be returned
    '''
    @patch('builtins.input', side_effect=['http://someurl'])
    def test_http_returns_no_certificate(self, mock_input):
        init_controller = InitController(self.conjurrc_data,self.init_logic, self.force_overwrite)
        fetched_certificate = init_controller.get_server_certificate()
        self.assertEquals(fetched_certificate, None)

    @patch('builtins.input', side_effect=['http://someurl'])
    def test_user_supplied_certificate_returns_none(self, mock_input):
        self.conjurrc_data.cert_file = "/some/path/somepem.pem"
        init_controller = InitController(self.conjurrc_data,self.init_logic, self.force_overwrite)
        fetched_certificate = init_controller.get_server_certificate()

        assert self.conjurrc_data.cert_file == "/some/path/somepem.pem"
        self.assertEquals(fetched_certificate, None)

    @patch('os.path.join')
    @patch('conjur.init.init_logic')
    def test_user_does_not_supply_cert_writes_to_file_called(self, mock_init_logic, mock_cert_path):
        self.conjurrc_data.appliance_url="https://someurl"

        mock_init_logic.write_certificate_to_file.return_value = None
        mock_cert_path.return_value = "/some/path/somepem.pem"
        InitController.write_certificate(self, mock_init_logic, self.conjurrc_data, None, "-----BEGIN CERTIFICATE-----")

        assert self.conjurrc_data.cert_file == mock_cert_path.return_value
        mock_init_logic.write_certificate_to_file.assert_called_once()


    @patch('conjur.init.init_logic')
    def test_user_supplies_cert_writes_to_file_not_called(self, mock_init_logic):
        InitController.write_certificate(self, mock_init_logic, self.conjurrc_data, "https://some/cert/path", None)
        mock_init_logic.write_certificate_to_file.assert_not_called()
