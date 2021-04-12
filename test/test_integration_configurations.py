# -*- coding: utf-8 -*-

"""
CLI Integration Configuration tests

This test file handles the configuration test flows when running
`conjur init`
"""
import os
from unittest.mock import patch

import requests

from conjur.data_object import CredentialsData
from conjur.logic.credential_provider import CredentialStoreFactory
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils

from conjur.constants import DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_FILE, DEFAULT_NETRC_FILE
from test.util.models.configfile import ConfigFile


class CliIntegrationTestConfigurations(IntegrationTestCaseBase):
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestConfigurations, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setUp(self):
        self.setup_cli_params({})
        utils.remove_file(DEFAULT_CONFIG_FILE)
        utils.remove_file(DEFAULT_CERTIFICATE_FILE)

    def print_instead_of_raise_error(self, error_class, error_message_regex, exit_code):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['list'], exit_code=exit_code)
        self.assertRegex(output, error_message_regex)

    def evoke_list(self, exit_code=0):
        return self.invoke_cli(self.cli_auth_params,
                               ['list'], exit_code=exit_code)

    # *************** INIT CONFIGURATION TESTS ***************

    '''
    Validates that the conjurrc cert_file entry is blank when run in --insecure mode
    '''
    @integration_test(True)
    @patch('builtins.input', return_value='yes')
    def test_https_conjurrc_in_insecure_mode_leaves_cert_file_empty(self, mock_input):
        self.setup_cli_params({})
        self.invoke_cli(self.cli_auth_params,
                        ['--insecure', 'init', '--url', self.client_params.hostname, '--account', 'someaccount'])

        utils.verify_conjurrc_contents('someaccount', self.client_params.hostname, '')

    '''
    Validates that certificate flag is overwritten when running in --insecure mode
    '''
    @integration_test(True)
    @patch('builtins.input', return_value='yes')
    def test_https_conjurrc_provided_cert_file_path_is_overwritten_in_insecure_mode(self, mock_input):
        self.setup_cli_params({})
        self.invoke_cli(self.cli_auth_params,
                        ['--insecure', 'init', '--url', self.client_params.hostname, '--account', 'someaccount',
                         '--certificate', self.environment.path_provider.certificate_path])

        utils.verify_conjurrc_contents('someaccount', self.client_params.hostname, '')

    '''
    Validates that the conjurrc was created on the machine
    '''
    @integration_test(True)
    @patch('builtins.input', return_value='yes')
    def test_https_conjurrc_is_created_with_all_parameters_given(self, mock_input):
        self.setup_cli_params({})
        self.invoke_cli(self.cli_auth_params,
                        ['init', '--url', self.client_params.hostname, '--account', 'someaccount'])

        utils.verify_conjurrc_contents('someaccount', self.client_params.hostname,
                                       self.environment.path_provider.certificate_path)
        assert os.path.isfile(DEFAULT_CERTIFICATE_FILE)

    '''
    Validates that the conjurrc was created on the machine when user provides Y instead of 'yes'
    '''
    @integration_test(True)
    @patch('builtins.input', return_value='Y')
    def test_https_conjurrc_is_created_when_user_provides_y_instead_of_yes(self, mock_input):
        self.setup_cli_params({})
        self.invoke_cli(self.cli_auth_params,
                        ['init', '--url', self.client_params.hostname, '--account', 'someaccount'])

        utils.verify_conjurrc_contents('someaccount', self.client_params.hostname,
                                       self.environment.path_provider.certificate_path)
        assert os.path.isfile(DEFAULT_CERTIFICATE_FILE)

    '''
    Validates that the conjurrc was created on the machine when user provides Y instead of 'yes' 
    when prompted to overwrite the conjurrc file
    '''
    @integration_test(True)
    def test_https_conjurrc_is_created_when_user_provides_y_instead_of_yes_for_overwrite(self):
        self.setup_cli_params({})
        with patch('builtins.input', side_effect=['Y', 'Y', 'Y', 'Y']):
            self.invoke_cli(self.cli_auth_params,
                            ['init', '--url', self.client_params.hostname, '--account', 'someaccount'])
        # Intentional double init here to test that the overwriting of the file prompt can take 'Y'
        with patch('builtins.input', side_effect=['Y', 'Y', 'Y', 'Y']):
            self.invoke_cli(self.cli_auth_params,
                            ['init', '--url', self.client_params.hostname, '--account', 'someaccount'])

        utils.verify_conjurrc_contents('someaccount', self.client_params.hostname,
                                       self.environment.path_provider.certificate_path)
        assert os.path.isfile(DEFAULT_CERTIFICATE_FILE)

    '''
    Validates that the conjurrc was created on the machine when a user mistakenly supplies an extra '/' at the end of the URL
    '''
    @integration_test()
    @patch('builtins.input', return_value='yes')
    def test_https_conjurrc_is_created_successfully_with_extra_slash_in_url(self, mock_input):
        self.setup_cli_params({})
        self.invoke_cli(self.cli_auth_params,
                        ['init', '--url', self.client_params.hostname + "/", '--account', 'someaccount'])

        utils.verify_conjurrc_contents('someaccount', self.client_params.hostname,
                                       self.environment.path_provider.certificate_path)
        assert os.path.isfile(DEFAULT_CERTIFICATE_FILE)

    '''
    Validates that if user does not trust the certificate,
    the conjurrc is not be created on the user's machine
    '''
    @integration_test(True)
    def test_https_conjurrc_user_does_not_trust_cert(self):
        with patch('builtins.input', side_effect=[self.client_params.hostname, 'no']):
            self.setup_cli_params({})
            output = self.invoke_cli(self.cli_auth_params,
                                     ['init'], exit_code=1)

            self.assertRegex(output, "You decided not to trust the certificate")
            assert not os.path.isfile(DEFAULT_CERTIFICATE_FILE)

    '''
    Validates that when the user adds the force flag,
    no confirmation is required
    '''
    @integration_test(True)
    # The additional side effects here ('somesideffect') would prompt the CLI to
    # request for confirmation which would fail the test
    @patch('builtins.input', side_effect=['yes', 'somesideeffect', 'somesideeffect'])
    def test_https_conjurrc_user_forces_overwrite_does_not_request_confirmation(self, mock_input):
        self.setup_cli_params({})
        output = self.invoke_cli(self.cli_auth_params,
                                 ['init', '--url', self.client_params.hostname, '--account', self.client_params.login,
                                  '--force'])

        assert "Not overwriting" not in output

    """
    DEVELOPER NOTE:
    This test should fail when running against a server with a CA-signed certificate configured.
    When a certificate can be validated against its own system's store, we don't actually use the 
    content of cert_file in the conjurrc when sending a request.
    See issue opened for this here: https://github.com/cyberark/conjur-api-python3/issues/209
    See flow description issue for more background info: https://github.com/cyberark/conjur-api-python3/issues/198
    """
    @integration_test(True)
    def test_https_cli_fails_if_cert_is_bad(self):
        # bad conjurrc
        conjurrc = ConfigFile(account=self.client_params.account, conjur_url=self.client_params.hostname,
                              cert_file=self.environment.path_provider.nginx_conf_path)
        conjurrc.dump_to_file()
        cred_store = utils.create_cred_store()
        credential_data = CredentialsData(machine=self.client_params.hostname,
                                          login="admin",
                                          password=self.client_params.env_api_key)
        cred_store.save(credential_data)
        self.setup_cli_params({})

        self.print_instead_of_raise_error(requests.exceptions.SSLError, "SSLError", exit_code=1)

    """
    DEVELOPER NOTE:
    This test should fail when running against a server with a CA-signed certificate configured.
    When a certificate can be validated against its own system's store, we don't actually use the 
    content of cert_file in the conjurrc when sending a request.
    See issue opened for this here: https://github.com/cyberark/conjur-api-python3/issues/209
    See flow description issue for more background info: https://github.com/cyberark/conjur-api-python3/issues/198
    """
    @integration_test(True)
    def test_https_cli_fails_if_cert_is_not_provided(self):
        conjurrc = ConfigFile(account=self.client_params.account, conjur_url=self.client_params.hostname,
                              cert_file="")
        conjurrc.dump_to_file()
        cred_store = utils.create_cred_store()
        credential_data = CredentialsData(machine=self.client_params.hostname,
                                          login="admin",
                                          password=self.client_params.env_api_key)
        cred_store.save(credential_data)
        self.setup_cli_params({})

        self.print_instead_of_raise_error(requests.exceptions.SSLError, "SSLError", exit_code=1)
