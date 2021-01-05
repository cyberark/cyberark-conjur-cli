# -*- coding: utf-8 -*-

"""
CLI Integration tests

This test file handles the main test flows after initialization and configuration
"""
import json
import tempfile
import uuid
import unittest
from unittest.mock import patch

from conjur.constants import *
from .util.cli_helpers import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase


# Not coverage tested since integration tests doesn't run in
# the same build step
class CliIntegrationTest(IntegrationTestCaseBase):  # pragma: no cover
    DEFINED_VARIABLE_ID = 'one/password'

    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTest, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************
    # Resets the conjurrc for the next run run
    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params

        return self.cli_auth_params

    @patch('builtins.input', return_value='yes')
    def init_to_cli(self, mock_input):
        self.invoke_cli(self.cli_auth_params,
                        ['init', '-u', self.client_params.hostname, '-a', self.client_params.account], exit_code=0)

    def setUp(self):
        self.setup_cli_params({})
        self.init_to_cli()
        with open(DEFAULT_NETRC_FILE, 'w') as netrc:
            netrc.write(f"machine {self.client_params.hostname}\n")
            netrc.write("login admin\n")
            netrc.write(f"password {self.client_params.env_api_key}\n")

        return self.invoke_cli(self.cli_auth_params,
                               ['policy', 'replace', 'root', self.environment.path_provider.get_policy_path("initial")])

    def set_variable(self, variable_id, value, exit_code=0):
        return self.invoke_cli(self.cli_auth_params,
                               ['variable', 'set', variable_id, value], exit_code=exit_code)

    def apply_policy(self, policy_path):
        return self.invoke_cli(self.cli_auth_params,
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
        return self.invoke_cli(self.cli_auth_params,
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
        return self.invoke_cli(self.cli_auth_params,
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
        return self.invoke_cli(self.cli_auth_params,
                               ['variable', 'get', *variable_ids])

    def assert_set_and_get(self, variable_id):
        expected_value = uuid.uuid4().hex

        self.set_variable(variable_id, expected_value)
        output = self.get_variable(variable_id)
        self.assertEquals(expected_value, output)

    def assert_variable_set_fails(self, variable_id, error_class, exit_code=0):
        with self.assertRaises(error_class):
            self.set_variable(variable_id, uuid.uuid4().hex, exit_code)

    def print_instead_of_raise_error(self, variable_id, error_message_regex):
        output = self.invoke_cli(self.cli_auth_params,
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
        output = self.invoke_cli(self.cli_auth_params,
                                 ['policy', 'apply', 'root', 'somepolicy.yml'], exit_code=1)
        self.assertRegex(output, "Error: No such file or directory:")

    '''
    A non-existent variable file will return a 404 Not Found error message
    '''

    @integration_test
    def test_unknown_secret_raises_not_found_error(self):
        output = self.invoke_cli(self.cli_auth_params,
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

        output = self.invoke_cli(self.cli_auth_params, ['list'])

        self.assertEquals(output,
                          f'[\n    "{self.client_params.account}:policy:root",\n    "{self.client_params.account}:variable:one/password"\n]\n')

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

        account_name = self.client_params.account
        expected_object = {
            'version': json_result['version'],
            'created_roles': {
                f'{account_name}:user:' + user_id1: {
                    'id': f'{account_name}:user:' + user_id1,
                    'api_key': json_result['created_roles'][f'{account_name}:user:' + user_id1]['api_key'],
                },
                f'{account_name}:user:' + user_id2: {
                    'id': f'{account_name}:user:' + user_id2,
                    'api_key': json_result['created_roles'][f'{account_name}:user:' + user_id2]['api_key'],
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
            self.print_instead_of_raise_error(old_variable, "404 Client Error: Not Found for url")

    @integration_test
    def test_https_replace_policy_can_output_returned_data(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)
        json_result = json.loads(self.replace_policy_from_string(policy))
        account_name = self.client_params.account

        expected_object = {
            'version': json_result['version'],
            'created_roles': {
                f'{account_name}:user:' + user_id1: {
                    'id': f'{account_name}:user:' + user_id1,
                    'api_key': json_result['created_roles'][f'{account_name}:user:' + user_id1]['api_key'],
                },
                f'{account_name}:user:' + user_id2: {
                    f'id': f'{account_name}:user:' + user_id2,
                    'api_key': json_result['created_roles'][f'{account_name}:user:' + user_id2]['api_key'],
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

        account_name = self.client_params.account
        expected_object = {
            'version': json_result['version'],
            'created_roles': {
                f'{account_name}:user:' + user_id1: {
                    'id': f'{account_name}:user:' + user_id1,
                    'api_key': json_result['created_roles'][f'{account_name}:user:' + user_id1]['api_key'],
                },
                f'{account_name}:user:' + user_id2: {
                    'id': f'{account_name}:user:' + user_id2,
                    'api_key': json_result['created_roles'][f'{account_name}:user:' + user_id2]['api_key'],
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

        output = self.invoke_cli(self.cli_auth_params, ['whoami'])
        response = json.loads(output)
        self.assertEquals(response.get('account'), f'{self.client_params.account}')
        self.assertEquals(response.get('username'), 'admin')