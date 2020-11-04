import json
import os
import tempfile
import uuid
import unittest

import requests

from .util.cli_helpers import integration_test, invoke_cli

from conjur.version import __version__


# Not coverage tested since integration tests doesn't run in
# the same build step
class CliIntegrationTest(unittest.TestCase): # pragma: no cover
    REQUIRED_ENV_VARS = {
        'CONJUR_ACCOUNT': 'account',
        'CONJUR_AUTHN_LOGIN': 'user',
        'CONJUR_AUTHN_API_KEY': 'password',
    }

    HTTP_ENV_VARS = {
        'CONJUR_HTTP_APPLIANCE_URL': 'url',
    }

    HTTPS_ENV_VARS = {
        'CONJUR_HTTPS_APPLIANCE_URL': 'url',
    }

    HTTPS_CA_BUNDLE_ENV_VAR = { 'CONJUR_CA_BUNDLE': 'ca-bundle' }

    DEFINED_VARIABLE_ID = 'one/password'


    # *************** HELPERS ***************

    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']

        cli_params_map = {**self.REQUIRED_ENV_VARS, **env_vars}
        for required_env_var, param_name in cli_params_map.items():
            self.assertIsNotNone(os.environ[required_env_var],
                    'ERROR: {} env var must be available for this test to work!'.format(required_env_var))
            self.assertGreater(len(os.environ[required_env_var]), 0,
                    'ERROR: {} env var must have a valid value for this test to work!'.format(required_env_var))

            self.cli_auth_params += ['--{}'.format(param_name), os.environ[required_env_var]]

        self.cli_auth_params += params

        return self.cli_auth_params

    def setUp(self):
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })
        return invoke_cli(self, self.cli_auth_params,
            ['policy', 'replace', 'root', 'test/test_config/initial_policy.yml'])

    def set_variable(self, variable_id, value):
        return invoke_cli(self, self.cli_auth_params,
            ['variable', 'set', variable_id, value])

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

    def assert_variable_set_fails(self, variable_id, error_class):
        with self.assertRaises(error_class):
            self.set_variable(variable_id,  uuid.uuid4().hex)

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

    @integration_test
    def test_http_cli_can_set_and_get_a_defined_variable(self):
        self.setup_cli_params(self.HTTP_ENV_VARS)
        self.assert_set_and_get(CliIntegrationTest.DEFINED_VARIABLE_ID)

    @integration_test
    def test_https_cli_can_set_and_get_a_defined_variable(self):
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

        self.assert_set_and_get(CliIntegrationTest.DEFINED_VARIABLE_ID)

    @integration_test
    def test_https_cli_can_set_and_get_a_defined_variable_if_cert_not_provided_and_verification_disabled(self):
        self.setup_cli_params(self.HTTPS_ENV_VARS, '--insecure')
        self.assert_set_and_get(CliIntegrationTest.DEFINED_VARIABLE_ID)

    @integration_test
    def test_https_cli_fails_if_cert_is_bad(self):
        self.setup_cli_params(self.HTTPS_ENV_VARS, '--ca-bundle', './test/test_config/https/nginx.conf')
        self.assert_variable_set_fails(CliIntegrationTest.DEFINED_VARIABLE_ID, requests.exceptions.SSLError)

    @integration_test
    def test_https_cli_fails_if_cert_is_not_provided(self):
        self.setup_cli_params(self.HTTPS_ENV_VARS)
        self.assert_variable_set_fails(CliIntegrationTest.DEFINED_VARIABLE_ID, requests.exceptions.SSLError)

    @integration_test
    def test_https_cli_can_batch_get_multiple_variables(self):
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

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
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

        output = invoke_cli(self, self.cli_auth_params, ['list'])

        self.assertEquals(output,
                          '[\n    "dev:policy:root",\n    "dev:variable:one/password"\n]\n')

    @integration_test
    def test_https_can_apply_policy(self):
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

        policy, variables = self.generate_policy_string()
        self.apply_policy_from_string(policy)

        for variable in variables:
            self.assert_set_and_get(variable)

    @integration_test
    def test_https_apply_policy_can_output_returned_data(self):
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

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
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

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
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

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
            self.assert_variable_set_fails(old_variable, requests.exceptions.HTTPError)

    @integration_test
    def test_https_replace_policy_can_output_returned_data(self):
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

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
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

        policy = "- !policy foo\n"
        json_result = json.loads(self.replace_policy_from_string(policy))

        expected_object = {
            'version': json_result['version'],
            'created_roles': {}
        }

        self.assertDictEqual(json_result, expected_object)


    @integration_test
    def test_https_can_delete_policy(self):
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

        policy, variables = self.generate_policy_string()
        self.delete_policy_from_string(policy)

        for variable in variables:
            self.assert_set_and_get(variable)

    @integration_test
    def test_https_delete_policy_can_output_returned_data(self):
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

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
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

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
        self.setup_cli_params({
            **self.HTTPS_ENV_VARS,
            **self.HTTPS_CA_BUNDLE_ENV_VAR
        })

        output = invoke_cli(self, self.cli_auth_params, ['whoami'])
        response = json.loads(output)
        self.assertEquals(response.get('account'), 'dev')
        self.assertEquals(response.get('username'), 'admin')
