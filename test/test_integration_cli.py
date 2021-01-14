# -*- coding: utf-8 -*-

"""
CLI Integration tests

This test file handles the main test flows after initialization and configuration
"""
import json
import tempfile
import uuid

import Utils
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

    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params

        return self.cli_auth_params

    def setUp(self):
        self.setup_cli_params({})
        Utils.setup_cli(self)
        return self.invoke_cli(self.cli_auth_params,
                               ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("initial")])

    # *************** TESTS ***************
    '''
    A non-existent policy file will return FileNotFound error message
    '''
    @integration_test
    def test_load_policy_raises_file_not_exists_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['policy', 'load', '-b', 'root', '-f', 'somepolicy.yml'], exit_code=1)
        self.assertRegex(output, "Error: No such file or directory:")

    @integration_test
    def test_https_can_load_policy(self):
        self.setup_cli_params({})

        policy, variables = Utils.generate_policy_string(self)
        Utils.load_policy_from_string(self, policy)

        for variable in variables:
            Utils.assert_set_and_get(self, variable)
    test_https_can_load_policy.tester=True
    @integration_test
    def test_https_load_policy_can_output_returned_data(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)

        # Run the new load that should not result in newly created roles
        json_result = json.loads(Utils.load_policy_from_string(self, policy))

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
    def test_https_load_policy_doesnt_break_if_no_created_roles(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)
        # Ensure that the accounts exist
        Utils.load_policy_from_string(self, policy)

        # Run the new load that should not result in newly created roles
        json_result = json.loads(Utils.load_policy_from_string(self, policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {}
        }

        self.assertDictEqual(json_result, expected_object)

    @integration_test
    def test_https_can_replace_policy(self):
        self.setup_cli_params({})

        orig_policy, old_variables = Utils.generate_policy_string(self)

        file_name=os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        with open(file_name, 'w+b') as temp_policy_file:
            temp_policy_file.write(orig_policy.encode('utf-8'))
            temp_policy_file.flush()

            Utils.load_policy(self, temp_policy_file.name)

        replacement_policy, new_variables = Utils.generate_policy_string(self)
        Utils.replace_policy_from_string(self, replacement_policy)

        for new_variable in new_variables:
            Utils.assert_set_and_get(self, new_variable)

        for old_variable in old_variables:
            Utils.print_instead_of_raise_error(self, old_variable, "404 Client Error: Not Found for url")
        os.remove(file_name)

    @integration_test
    def test_https_replace_policy_can_output_returned_data(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)
        json_result = json.loads(Utils.replace_policy_from_string(self, policy))
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
        json_result = json.loads(Utils.replace_policy_from_string(self, policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {}
        }

        self.assertDictEqual(json_result, expected_object)

    @integration_test
    def test_https_can_update_policy(self):
        self.setup_cli_params({})

        policy, variables = Utils.generate_policy_string(self)
        Utils.update_policy_from_string(self, policy)

        for variable in variables:
            Utils.assert_set_and_get(self, variable)

    @integration_test
    def test_https_update_policy_can_output_returned_data(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)

        # Run the new update that should not result in newly created roles
        json_result = json.loads(Utils.update_policy_from_string(self, policy))

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
    def test_https_update_policy_doesnt_break_if_no_created_roles(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)
        # Ensure that the accounts exist
        Utils.update_policy_from_string(self, policy)

        # Run the new load that should not result in newly created roles
        json_result = json.loads(Utils.update_policy_from_string(self, policy))

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
