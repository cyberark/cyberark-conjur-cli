# -*- coding: utf-8 -*-

"""
CLI Integration tests

This test file handles the main test flows after initialization and configuration
"""
import io
import json
import tempfile
import uuid
from contextlib import redirect_stderr

from conjur.constants import *
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils

# Not coverage tested since integration tests doesn't run in
# the same build step
class CliIntegrationPolicy(IntegrationTestCaseBase):  # pragma: no cover
    capture_stream = io.StringIO()
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationPolicy, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setUp(self):
        self.setup_cli_params({})
        utils.setup_cli(self)
        return self.invoke_cli(self.cli_auth_params,
                               ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("initial")])

    # *************** TESTS ***************

    @integration_test(True)
    def test_https_can_load_policy(self):
        self.setup_cli_params({})

        policy, variables = utils.generate_policy_string()
        utils.load_policy_from_string(self, policy)

        for variable in variables:
            utils.assert_set_and_get(self, variable)

    @integration_test()
    def test_load_policy_of_new_resources_returns_new_entry_json_data(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)

        # Run the new load that should not result in newly created roles
        json_result = json.loads(utils.load_policy_from_string(self, policy))

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

    '''
    Validates that a policy command without a subcommand 'load'
    in this case, will fail and return help screen
    '''
    @integration_test()
    def test_policy_load_without_subcommand_returns_help_screen(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                                     ['policy', '-b', 'root', '-f', 'somepolicy.yml'], exit_code=1)
        self.assertIn("Error argument action: invalid choice: 'root' (choose from", self.capture_stream.getvalue())

    '''
    Validates that a policy command without the policy path
    will fail and return help screen
    '''
    @integration_test()
    def test_policy_load_without_policy_path_returns_help_screen(self):
        with redirect_stderr(self.capture_stream):
            output = self.invoke_cli(self.cli_auth_params,
                           ['policy', 'load', '-b', 'root'], exit_code=1)
        self.assertIn("Error the following arguments are required", self.capture_stream.getvalue())

    '''
    A non-existent policy file will return FileNotFound error message
    '''
    @integration_test(True)
    def test_policy_load_raises_file_not_exists_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['policy', 'load', '-b', 'root', '-f', 'somenonexistantpolicy.yml'], exit_code=1)
        self.assertRegex(output, "Error: No such file or directory:")

    '''
    A policy with invalid syntax will return a Unprocessable entity error
    '''
    @integration_test()
    def test_policy_bad_syntax_raises_error(self):
        policy = "- ! user bad syntax"
        with self.assertLogs('', level='DEBUG') as mock_log:
            with redirect_stderr(self.capture_stream):
                output = utils.load_policy_from_string(self, policy, exit_code=1)
            self.assertIn("422 Client Error", output)
        self.assertIn("422 Unprocessable Entity {\"error\":{\"code\":\"validation_failed\",\"message\":",
                  str(mock_log.output))

    @integration_test()
    def test_policy_replace_load_combo_returns_help_screen(self):
        with redirect_stderr(self.capture_stream):
            output = self.invoke_cli(self.cli_auth_params,
                   ['policy', 'load', 'replace', '-b', 'root', '-f', 'somepolicy.yml'], exit_code=1)
        self.assertIn('Error unrecognized arguments: replace', self.capture_stream.getvalue())

    @integration_test()
    def test_policy_insecure_prints_warning_in_log(self):
        with self.assertLogs('', level='DEBUG') as mock_log:
            self.invoke_cli(self.cli_auth_params,
                               ['--insecure', 'policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("initial")])

            self.assertIn("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks",
                          str(mock_log.output))

    @integration_test(True)
    def test_policy_replace_bad_syntax_raises_error(self):
        policy = "- ! user bad syntax"
        output = utils.replace_policy_from_string(self, policy, exit_code=1)

        self.assertIn("422 Client Error", output)

    @integration_test()
    def test_https_load_policy_doesnt_break_if_no_created_roles(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)
        # Ensure that the accounts exist
        utils.load_policy_from_string(self, policy)

        # Run the new load that should not result in newly created roles
        json_result = json.loads(utils.load_policy_from_string(self, policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {}
        }

        self.assertDictEqual(json_result, expected_object)

    @integration_test(True)
    def test_https_can_replace_policy(self):
        self.setup_cli_params({})

        orig_policy, old_variables = utils.generate_policy_string()

        file_name=os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        with open(file_name, 'w+b') as temp_policy_file:
            temp_policy_file.write(orig_policy.encode('utf-8'))
            temp_policy_file.flush()

            utils.load_policy(self, temp_policy_file.name)

        replacement_policy, new_variables = utils.generate_policy_string()
        utils.replace_policy_from_string(self, replacement_policy)

        for new_variable in new_variables:
            utils.assert_set_and_get(self, new_variable)

        for old_variable in old_variables:
            utils.print_instead_of_raise_error(self, old_variable, "404 Client Error: Not Found for url")
        os.remove(file_name)

    @integration_test()
    def test_https_replace_policy_can_output_returned_data(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)
        json_result = json.loads(utils.replace_policy_from_string(self, policy))
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

    @integration_test()
    def test_https_replace_policy_doesnt_break_if_no_created_roles(self):
        self.setup_cli_params({})

        policy = "- !policy foo\n"
        json_result = json.loads(utils.replace_policy_from_string(self, policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {}
        }

        self.assertDictEqual(json_result, expected_object)

    @integration_test(True)
    def test_https_can_update_policy(self):
        self.setup_cli_params({})

        policy, variables = utils.generate_policy_string()
        utils.update_policy_from_string(self, policy)

        for variable in variables:
            utils.assert_set_and_get(self, variable)

    @integration_test()
    def test_https_update_policy_can_output_returned_data(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)

        # Run the new update that should not result in newly created roles
        json_result = json.loads(utils.update_policy_from_string(self, policy))

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

    @integration_test()
    def test_https_update_policy_doesnt_break_if_no_created_roles(self):
        self.setup_cli_params({})

        user_id1 = uuid.uuid4().hex
        user_id2 = uuid.uuid4().hex
        policy = "- !user {user_id1}\n- !user {user_id2}\n".format(user_id1=user_id1,
                                                                   user_id2=user_id2)
        # Ensure that the accounts exist
        utils.update_policy_from_string(self, policy)

        # Run the new load that should not result in newly created roles
        json_result = json.loads(utils.update_policy_from_string(self, policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {}
        }

        self.assertDictEqual(json_result, expected_object)

    '''
    Validates that update deletes record
    '''
    @integration_test()
    def test_policy_update_policy_removes_user(self):
        user_id = uuid.uuid4().hex

        load_policy = f"- !user {user_id}"
        json.loads(utils.load_policy_from_string(self, load_policy))
        update_policy = f"- !delete\n record: !user {user_id}"
        json.loads(utils.update_policy_from_string(self, update_policy))

        output = self.invoke_cli(self.cli_auth_params, ['list'])

        # Assert that user_id is not in output
        self.assertTrue(output.find(user_id) == -1)


    @integration_test()
    def test_https_can_get_whoami(self):
        self.setup_cli_params({})

        output = self.invoke_cli(self.cli_auth_params, ['whoami'])
        response = json.loads(output)
        self.assertIn(f'{self.client_params.account}', response.get('account'))
        self.assertIn('admin', response.get('username'))

    @integration_test()
    def test_insecure_https_can_get_whoami(self):
        self.setup_insecure()
        output = self.invoke_cli(self.cli_auth_params, ['whoami'])
        response = json.loads(output)
        self.assertIn(f'{self.client_params.account}', response.get('account'))
        self.assertIn('admin', response.get('username'))

    @integration_test()
    def test_https_can_get_whoami_insecure(self):
        self.setup_insecure()
        output = self.invoke_cli(self.cli_auth_params, ['whoami'])
        response = json.loads(output)
        self.assertIn(f'{self.client_params.account}', response.get('account'))
        self.assertIn('admin', response.get('username'))

