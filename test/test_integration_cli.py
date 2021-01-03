# -*- coding: utf-8 -*-

"""
CLI Integration tests

This test file has two separate classes to cover two different client flows.
The first class is for testing configurations of the CLI. The second
assumes the client has been initialized.
"""
import base64
import json
import os
import shutil
import tempfile
import uuid
import unittest
from unittest.mock import patch

import requests

from .util.cli_helpers import integration_test, invoke_cli

from conjur.constants import DEFAULT_NETRC_FILE, DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_FILE, TEST_HOSTNAME

class CliIntegrationTestCredentials(unittest.TestCase):
    # *************** HELPERS ***************

    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params

        return self.cli_auth_params

    def setUp(self):
        self.setup_cli_params({})
        os.system(f'rm -f {DEFAULT_NETRC_FILE}')
        os.system(f'rm -f {DEFAULT_CONFIG_FILE}')
        os.system(f'rm -f {DEFAULT_CERTIFICATE_FILE}')

    # *************** INITIAL LOGIN CREDENTIALS TESTS ***************

    '''
    Validates we can login with a password, instead of an API key
    Note that to do this we need to create a password for the admin
    and validate that the netrc file was properly created
    '''
    @integration_test
    def test_https_netrc_is_created_with_all_parameters_given(self):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'admin', '-p', os.environ['CONJUR_AUTHN_API_KEY']], exit_code=0)

        payload="@Sup3rS3cr3t@"
        combo = base64.b64encode(f"admin:{os.environ['CONJUR_AUTHN_API_KEY']}".encode("utf-8"))
        headers = {
          'Authorization': f'Basic {str(combo, "utf-8")}',
          'Content-Type': 'text/plain'
        }

        requests.request("PUT", f"{TEST_HOSTNAME}/authn/dev/password", headers=headers, data=payload, verify="/opt/conjur-api-python3/test/test_config/https/ca.crt")

        # Need to remove the netrc because we are attempting to login with new password
        os.system(f'rm -f {DEFAULT_NETRC_FILE}')
        output = invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'admin', '-p', payload], exit_code=0)

        self.assertEquals(output.strip(), "Successfully logged in to Conjur")
        with open(DEFAULT_NETRC_FILE, 'r') as netrc:
            lines = netrc.readlines()
            assert f"machine {TEST_HOSTNAME}/authn" in lines[0]
            assert "login admin" in lines[1]
            assert f"password {os.environ['CONJUR_AUTHN_API_KEY']}" in lines[2]

    '''
    Validates interactively provided params create netrc
    '''
    @integration_test
    @patch('builtins.input', return_value='admin')
    @patch('getpass.getpass', return_value=os.environ['CONJUR_AUTHN_API_KEY'])
    def test_https_netrc_is_created_with_all_parameters_given_interactively(self, mock_pass, mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        output = invoke_cli(self, self.cli_auth_params,
            ['login'], exit_code=0)

        assert os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0
        self.assertEquals(output.strip(), "Successfully logged in to Conjur")

        with open(DEFAULT_NETRC_FILE, 'r') as netrc:
            lines = netrc.readlines()
            assert f"machine {TEST_HOSTNAME}/authn" in lines[0]
            assert "login admin" in lines[1]
            assert f"password {os.environ['CONJUR_AUTHN_API_KEY']}" in lines[2]

    '''
    Validates a wrong username will raise Unauthorized error
    '''
    @integration_test
    @patch('builtins.input', return_value='somebaduser')
    @patch('getpass.getpass', return_value=os.environ['CONJUR_AUTHN_API_KEY'])
    def test_https_netrc_raises_error_with_wrong_user(self, mock_pass, mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        output = invoke_cli(self, self.cli_auth_params,
            ['login'], exit_code=1)

        self.assertRegex(output, "Reason: 401 Client Error: Unauthorized for")
        assert not os.path.exists(DEFAULT_NETRC_FILE)

    '''
    Validates a wrong password will raise Unauthorized error
    '''
    @integration_test
    @patch('builtins.input', return_value='admin')
    @patch('getpass.getpass', return_value='somewrongpass')
    def test_https_netrc_with_wrong_password(self, mock_pass, mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        output = invoke_cli(self, self.cli_auth_params,
            ['login'], exit_code=1)

        self.assertRegex(output, "Reason: 401 Client Error: Unauthorized for")
        assert not os.path.exists(DEFAULT_NETRC_FILE)

    @integration_test
    @patch('builtins.input', return_value='admin')
    @patch('getpass.getpass', return_value=os.environ['CONJUR_AUTHN_API_KEY'])
    def test_https_netrc_is_created_when_provided_user_api_key(self, mock_pass, mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        output = invoke_cli(self, self.cli_auth_params,
            ['login'], exit_code=0)

        assert os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0
        self.assertEquals(output.strip(), "Successfully logged in to Conjur")

        with open(DEFAULT_NETRC_FILE, 'r') as netrc:
            lines = netrc.readlines()
            assert f"machine {TEST_HOSTNAME}/authn" in lines[0]
            assert "login admin" in lines[1]
            assert f"password {os.environ['CONJUR_AUTHN_API_KEY']}" in lines[2]

    '''
    Validates that when a user already logged in and reattempts and fails, the previous successful session is not removed
    '''
    @integration_test
    def test_https_netrc_was_not_overwritten_when_login_failed_but_already_logged_in(self):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        successful_run = invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'admin', '-p', os.environ['CONJUR_AUTHN_API_KEY']], exit_code=0)
        self.assertEquals(successful_run.strip(), "Successfully logged in to Conjur")

        unsuccessful_run = invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'someinvaliduser', '-p', 'somewrongpassword'], exit_code=1)
        self.assertRegex(unsuccessful_run, "Reason: 401 Client Error: Unauthorized for")

        with open(DEFAULT_NETRC_FILE, 'r') as netrc:
            lines = netrc.readlines()
            assert f"machine {TEST_HOSTNAME}/authn" in lines[0]
            assert "login admin" in lines[1]
            assert f"password {os.environ['CONJUR_AUTHN_API_KEY']}" in lines[2]

    '''
    Validates login is successful for hosts
    
    Note we need to create the host first and rotate it's API key so that we can access it.
    There is currently no way to fetch a host's API key so this is a work around for the 
    purposes of this test
    '''
    @integration_test
    def test_https_netrc_is_created_with_host(self):
        # Setup for fetching the API key of a host. To fetch we need to login
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        with open(f"{DEFAULT_NETRC_FILE}", "w") as netrc_test:
            netrc_test.write(f"machine {TEST_HOSTNAME}/authn\n")
            netrc_test.write("login admin\n")
            netrc_test.write(f"password {os.environ['CONJUR_AUTHN_API_KEY']}\n")

        invoke_cli(self, self.cli_auth_params,
                   ['policy', 'replace', 'root', 'test/test_config/host_policy.yml'], exit_code=0)

        url = f"{TEST_HOSTNAME}/authn/dev/admin/authenticate"
        headers = {
          'Content-Type': 'text/plain'
        }

        response = requests.request("POST", url, headers=headers, data=os.environ['CONJUR_AUTHN_API_KEY'], verify="/opt/conjur-api-python3/test/test_config/https/ca.crt")
        access_token = base64.b64encode(response.content).decode("utf-8")

        headers = {
          'Authorization': f'Token token="{access_token}"'
        }
        url = f"{TEST_HOSTNAME}/authn/dev/api_key?role=host:somehost"
        # We want to rotate the API key of the host so we will know the value
        host_api_key = requests.request("PUT", url, headers=headers, data=os.environ['CONJUR_AUTHN_API_KEY'], verify="/opt/conjur-api-python3/test/test_config/https/ca.crt").text

        os.system(f'rm -f {DEFAULT_NETRC_FILE}')

        output = invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'host/somehost', '-p', f'{host_api_key}'], exit_code=0)

        with open(DEFAULT_NETRC_FILE, 'r') as netrc:
            lines = netrc.readlines()
            assert f"machine {TEST_HOSTNAME}/authn" in lines[0]
            assert "login host/somehost" in lines[1]
            assert f"password {host_api_key}" in lines[2]
        self.assertEquals(output.strip(), "Successfully logged in to Conjur")

    '''
    Validates when a user can logout successfully
    '''
    @integration_test
    def test_https_logout_successful(self):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')
        invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'admin', '-p', os.environ['CONJUR_AUTHN_API_KEY']], exit_code=0)
        assert os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0

        output = invoke_cli(self, self.cli_auth_params,
            ['logout'], exit_code=0)

        self.assertEquals(output.strip(), 'Logged out from Conjur')
        assert os.path.getsize(DEFAULT_NETRC_FILE) == 0

    '''
    Validates when a user attempts to logout after an already 
    successful logout, will fail
    '''
    @integration_test
    def test_https_logout_twice_returns_could_not_logout_message(self):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'admin', '-p', os.environ['CONJUR_AUTHN_API_KEY']], exit_code=0)

        invoke_cli(self, self.cli_auth_params,
            ['logout'], exit_code=0)

        unsuccessful_logout = invoke_cli(self, self.cli_auth_params,
            ['logout'], exit_code=1)

        self.assertEquals(unsuccessful_logout.strip(), "Failed to logout. Please log in")
        assert os.path.getsize(DEFAULT_NETRC_FILE) == 0

    @integration_test
    def test_no_netrc_and_logout_returns_could_not_logout_message(self):
        os.system(f'rm -f {DEFAULT_NETRC_FILE}')
        unsuccessful_logout = invoke_cli(self, self.cli_auth_params,
            ['logout'], exit_code=1)
        self.assertEquals(unsuccessful_logout.strip(), "Failed to logout. Please log in")

    '''
    Validates that when the user does not log in and attempt
    to interface with the CLI, they will be prompted to
    '''
    @integration_test
    @patch('builtins.input', return_value='someaccount')
    @patch('getpass.getpass', return_value='somepass')
    def test_user_runs_list_without_netrc_prompts_user_to_login(self, mock_pass, mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        list_attempt = invoke_cli(self, self.cli_auth_params,
            ['list'], exit_code=1)
        self.assertRegex(list_attempt.strip(), "Unable to authenticate with Conjur.")

class CliIntegrationTestConfigurations(unittest.TestCase):

    # *************** HELPERS ***************

    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params

        return self.cli_auth_params

    def setUp(self):
        self.setup_cli_params({})
        os.system(f'rm -f {DEFAULT_CONFIG_FILE}')
        os.system(f'rm -f {DEFAULT_CERTIFICATE_FILE}')

    def print_instead_of_raise_error(self, error_class, error_message_regex, exit_code):
        output = invoke_cli(self, self.cli_auth_params,
            ['list'], exit_code=exit_code)
        self.assertRegex(output, error_message_regex)

    def evoke_list(self, exit_code=0):
        return invoke_cli(self, self.cli_auth_params,
            ['list'], exit_code=exit_code)

    # *************** INITIAL INIT CONFIGURATION TESTS ***************

    '''
    Validates that the conjurrc was created on the machine
    '''
    @integration_test
    @patch('builtins.input', return_value='yes')
    def test_https_conjurrc_is_created_with_all_parameters_given(self, mock_input):
        self.setup_cli_params({})
        invoke_cli(self, self.cli_auth_params,
            ['init', '--url', TEST_HOSTNAME, '--account', 'someaccount'], exit_code=0)

        assert os.path.isfile("/root/.conjurrc")

    '''
    Validates that when passed as commandline arguments, the configuration
    data is written properly to conjurrc. 
    
    Note that this test should return a warning because we are working against 
    OSS that doesn't have the /info endpoint
    '''
    @integration_test
    @patch('builtins.input', side_effect=[TEST_HOSTNAME, 'yes', 'someotheraccount'])
    def test_https_conjurrc_is_created_with_no_parameters_given(self, mock_input):
        self.setup_cli_params({})
        invoke_cli(self, self.cli_auth_params,
            ['init'], exit_code=0)

        with open(f"{DEFAULT_CONFIG_FILE}", 'r') as conjurrc:
            lines = conjurrc.readlines()
            assert "---" in lines[0]
            assert "account: someotheraccount" in lines[1]
            assert f"appliance_url: {TEST_HOSTNAME}" in lines[2]

    '''
    Validates that if user does not trust the certificate,
    the conjurrc is not be created on the user's machine
    '''
    @integration_test
    @patch('builtins.input', side_effect=[TEST_HOSTNAME, 'no'])
    def test_https_conjurrc_user_does_not_trust_cert(self, mock_input):
        self.setup_cli_params({})
        output = invoke_cli(self, self.cli_auth_params,
            ['init'], exit_code=1)

        self.assertRegex(output, "You decided not to trust the certificate")
        assert not os.path.isfile("/root/.conjurrc")

    '''
    Validates that when the user adds the force flag,
    no confirmation is required
    '''
    @integration_test
    # The additional side effects here ('somesideffect') would prompt the CLI to
    # request for confirmation which would fail the test
    @patch('builtins.input', side_effect=['yes', 'somesideeffect', 'somesideeffect'])
    def test_https_conjurrc_user_forces_overwrite_does_not_request_confirmation(self, mock_input):
        self.setup_cli_params({})
        output = invoke_cli(self, self.cli_auth_params,
            ['init', '--url', TEST_HOSTNAME, '--account', 'dev', '--force'], exit_code=0)

        assert "Not overwriting" not in output

    @integration_test
    def test_https_cli_fails_if_cert_is_bad(self):
        shutil.copy('./test/test_config/bad_cert_conjurrc', f'{DEFAULT_CONFIG_FILE}')
        self.setup_cli_params({})
        self.print_instead_of_raise_error(requests.exceptions.SSLError, "SSLError", exit_code=1)

    @integration_test
    def test_https_cli_fails_if_cert_is_not_provided(self):
        shutil.copy('./test/test_config/no_cert_conjurrc', f'{DEFAULT_CONFIG_FILE}')
        self.setup_cli_params({})
        self.print_instead_of_raise_error(requests.exceptions.SSLError, "SSLError", exit_code=1)

# Not coverage tested since integration tests doesn't run in
# the same build step
class CliIntegrationTest(unittest.TestCase): # pragma: no cover
    shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')
    DEFINED_VARIABLE_ID = 'one/password'

    # *************** HELPERS ***************
    # Resets the conjurrc for the next run run
    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params

        return self.cli_auth_params

    def setUp(self):
        self.setup_cli_params({})

        with open(DEFAULT_NETRC_FILE, 'w') as netrc:
            netrc.write(f"machine {TEST_HOSTNAME}\n")
            netrc.write("login admin\n")
            netrc.write(f"password {os.environ['CONJUR_AUTHN_API_KEY']}\n")

        return invoke_cli(self, self.cli_auth_params,
            ['policy', 'replace', 'root', 'test/test_config/initial_policy.yml'])

    def set_variable(self, variable_id, value, exit_code=0):
        return invoke_cli(self, self.cli_auth_params,
            ['variable', 'set', variable_id, value], exit_code=exit_code)

    def apply_policy(self, policy_path):
        return invoke_cli(self, self.cli_auth_params,
            ['policy', 'apply', 'root', policy_path])

    def apply_policy_from_string(self, policy):
        output = None
        with tempfile.NamedTemporaryFile() as temp_policy_file:
            temp_policy_file.write(policy.encode('utf-8'))
            temp_policy_file.flush()

            # Run the new apply that should not result in newly created roles
            output = self.apply_policy(temp_policy_file.name)

        return output

    def replace_policy(self, policy_path):
        return invoke_cli(self, self.cli_auth_params,
            ['policy', 'replace', 'root', policy_path])

    def replace_policy_from_string(self, policy):
        output = None
        with tempfile.NamedTemporaryFile() as temp_policy_file:
            temp_policy_file.write(policy.encode('utf-8'))
            temp_policy_file.flush()

            # Run the new replace that should not result in newly created roles
            output = self.replace_policy(temp_policy_file.name)

        return output

    def delete_policy(self, policy_path):
        return invoke_cli(self, self.cli_auth_params,
            ['policy', 'delete', 'root', policy_path])

    def delete_policy_from_string(self, policy):
        output = None
        with tempfile.NamedTemporaryFile() as temp_policy_file:
            temp_policy_file.write(policy.encode('utf-8'))
            temp_policy_file.flush()

            # Run the new delete that should not result in newly created roles
            output = self.delete_policy(temp_policy_file.name)

        return output

    def get_variable(self, *variable_ids):
        return invoke_cli(self, self.cli_auth_params,
            ['variable', 'get', *variable_ids])

    def assert_set_and_get(self, variable_id):
        expected_value = uuid.uuid4().hex

        self.set_variable(variable_id, expected_value)
        output = self.get_variable(variable_id)
        self.assertEquals(expected_value, output)

    def assert_variable_set_fails(self, variable_id, error_class, exit_code=0):
        with self.assertRaises(error_class):
            self.set_variable(variable_id,  uuid.uuid4().hex, exit_code)

    def print_instead_of_raise_error(self, variable_id, error_message_regex):
        output = invoke_cli(self,  self.cli_auth_params,
            ['variable', 'set', variable_id, uuid.uuid4().hex], exit_code=1)

        self.assertRegex(output, error_message_regex)

    def generate_policy_string(self):
        variable_1 = 'simple/basic/{}'.format(uuid.uuid4().hex)
        variable_2 = 'simple/space filled/{}'.format(uuid.uuid4().hex)
        variable_3 = 'simple/special @#$%^&*(){{}}[]._+/{id}'.format(id=uuid.uuid4().hex)

        policy = \
"""
- !variable
  id: {variable_1}
- !variable
  id: {variable_2}
- !variable
  id: {variable_3}
"""

        dynamic_policy = policy.format(variable_1=variable_1,
                                       variable_2=variable_2,
                                       variable_3=variable_3)

        return (dynamic_policy, [variable_1, variable_2, variable_3])


    # *************** TESTS ***************
    '''
    A non-existent policy file will return FileNotFound error message
    '''
    @integration_test
    def test_apply_policy_raises_file_not_exists_error(self):
        output = invoke_cli(self, self.cli_auth_params,
            ['policy', 'apply', 'root', 'somepolicy.yml'], exit_code=1)
        self.assertRegex(output, "Error: No such file or directory:")

    '''
    A non-existent variable file will return a 404 Not Found error message
    '''
    @integration_test
    def test_unknown_secret_raises_not_found_error(self):
        output = invoke_cli(self, self.cli_auth_params,
            ['variable', 'get', 'unknown'], exit_code=1)
        self.assertRegex(output, "404 Client Error: Not Found for url:")

    @integration_test
    def test_https_cli_can_set_and_get_a_defined_variable(self):
        self.setup_cli_params({})

        self.assert_set_and_get(CliIntegrationTest.DEFINED_VARIABLE_ID)

    @integration_test
    def test_https_cli_can_set_and_get_a_defined_variable_if_cert_not_provided_and_verification_disabled(self):
        self.setup_cli_params({}, '--insecure')
        self.assert_set_and_get(CliIntegrationTest.DEFINED_VARIABLE_ID)

    @integration_test
    def test_https_cli_can_batch_get_multiple_variables(self):
        self.setup_cli_params({})

        policy, variables = self.generate_policy_string()
        with tempfile.NamedTemporaryFile() as temp_policy_file:
            temp_policy_file.write(policy.encode('utf-8'))
            temp_policy_file.flush()

            self.apply_policy(temp_policy_file.name)

        value_map = {}
        for variable in variables:
            value = uuid.uuid4().hex
            self.set_variable(variable, value)
            value_map[variable] = value

        batch_result_string = self.get_variable(*variables)
        batch_result = json.loads(batch_result_string)

        for variable_name, variable_value in value_map.items():
            self.assertEquals(variable_value, batch_result[variable_name])

    @integration_test
    def test_https_can_list_resources(self):
        self.setup_cli_params({})

        output = invoke_cli(self, self.cli_auth_params, ['list'])

        self.assertEquals(output,
                          '[\n    "dev:policy:root",\n    "dev:variable:one/password"\n]\n')

    @integration_test
    def test_https_can_apply_policy(self):
        self.setup_cli_params({})

        policy, variables = self.generate_policy_string()
        self.apply_policy_from_string(policy)

        for variable in variables:
            self.assert_set_and_get(variable)

    @integration_test
    def test_https_apply_policy_can_output_returned_data(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)

        # Run the new apply that should not result in newly created roles
        json_result = json.loads(self.apply_policy_from_string(policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {
                'dev:user:' + user_id1: {
                    'id': 'dev:user:' + user_id1,
                    'api_key': json_result['created_roles']['dev:user:' + user_id1]['api_key'],
                },
                'dev:user:' + user_id2: {
                    'id': 'dev:user:' + user_id2,
                    'api_key': json_result['created_roles']['dev:user:' + user_id2]['api_key'],
                }
            }
        }

        self.assertDictEqual(json_result, expected_object)

    @integration_test
    def test_https_apply_policy_doesnt_break_if_no_created_roles(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)
        # Ensure that the accounts exist
        self.apply_policy_from_string(policy)

        # Run the new apply that should not result in newly created roles
        json_result = json.loads(self.apply_policy_from_string(policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {}
        }

        self.assertDictEqual(json_result, expected_object)

    @integration_test
    def test_https_can_replace_policy(self):
        self.setup_cli_params({})

        orig_policy, old_variables = self.generate_policy_string()

        with tempfile.NamedTemporaryFile() as temp_policy_file:
            temp_policy_file.write(orig_policy.encode('utf-8'))
            temp_policy_file.flush()

            self.apply_policy(temp_policy_file.name)

        replacement_policy, new_variables = self.generate_policy_string()
        self.replace_policy_from_string(replacement_policy)

        for new_variable in new_variables:
            self.assert_set_and_get(new_variable)

        for old_variable in old_variables:
            self.print_instead_of_raise_error(old_variable,  "404 Client Error: Not Found for url")

    @integration_test
    def test_https_replace_policy_can_output_returned_data(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)
        json_result = json.loads(self.replace_policy_from_string(policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {
                'dev:user:' + user_id1: {
                    'id': 'dev:user:' + user_id1,
                    'api_key': json_result['created_roles']['dev:user:' + user_id1]['api_key'],
                },
                'dev:user:' + user_id2: {
                    'id': 'dev:user:' + user_id2,
                    'api_key': json_result['created_roles']['dev:user:' + user_id2]['api_key'],
                }
            }
        }

        self.assertDictEqual(json_result, expected_object)

    @integration_test
    def test_https_replace_policy_doesnt_break_if_no_created_roles(self):
        self.setup_cli_params({})

        policy = "- !policy foo\n"
        json_result = json.loads(self.replace_policy_from_string(policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {}
        }

        self.assertDictEqual(json_result, expected_object)


    @integration_test
    def test_https_can_delete_policy(self):
        self.setup_cli_params({})

        policy, variables = self.generate_policy_string()
        self.delete_policy_from_string(policy)

        for variable in variables:
            self.assert_set_and_get(variable)

    @integration_test
    def test_https_delete_policy_can_output_returned_data(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)

        # Run the new delete that should not result in newly created roles
        json_result = json.loads(self.delete_policy_from_string(policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {
                'dev:user:' + user_id1: {
                    'id': 'dev:user:' + user_id1,
                    'api_key': json_result['created_roles']['dev:user:' + user_id1]['api_key'],
                },
                'dev:user:' + user_id2: {
                    'id': 'dev:user:' + user_id2,
                    'api_key': json_result['created_roles']['dev:user:' + user_id2]['api_key'],
                }
            }
        }

        self.assertDictEqual(json_result, expected_object)

    @integration_test
    def test_https_delete_policy_doesnt_break_if_no_created_roles(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)
        # Ensure that the accounts exist
        self.delete_policy_from_string(policy)

        # Run the new apply that should not result in newly created roles
        json_result = json.loads(self.delete_policy_from_string(policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {}
        }

        self.assertDictEqual(json_result, expected_object)

    @integration_test
    def test_https_can_get_whoami(self):
        self.setup_cli_params({})

        output = invoke_cli(self, self.cli_auth_params, ['whoami'])
        response = json.loads(output)
        self.assertEquals(response.get('account'), 'dev')
        self.assertEquals(response.get('username'), 'admin')
