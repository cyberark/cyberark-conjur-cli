import os
import uuid
import unittest

from .util.cli_helpers import integration_test, invoke_cli

from conjur_api_python3.version import __version__


class CliIntegrationTest(unittest.TestCase):
    REQUIRED_ENV_VARS = {
        'CONJUR_APPLIANCE_URL': 'url',
        'CONJUR_ACCOUNT': 'account',
        'CONJUR_AUTHN_LOGIN': 'user',
        'CONJUR_AUTHN_API_KEY': 'api-key',
    }

    DEFINED_VARIABLE_ID = 'one/password'

    def setUp(self):
        self.cli_auth_params = ['--debug']
        for required_env_var, param_name in self.REQUIRED_ENV_VARS.items():
            self.assertIsNotNone(os.environ[required_env_var],
                    'ERROR: {} env var must be available for this test to work!'.format(required_env_var))
            self.assertGreater(len(os.environ[required_env_var]), 0,
                    'ERROR: {} env var must have a valid value for this test to work!'.format(required_env_var))

        # Dynamically create a static param list that is class-wide
        for required_env_var, param_name in self.REQUIRED_ENV_VARS.items():
            self.cli_auth_params += ['--{}'.format(param_name), os.environ[required_env_var]]

        # Reset variable "one/password"
        self.set_variable(CliIntegrationTest.DEFINED_VARIABLE_ID, 'garbagevalue')

    def set_variable(self, variable_id, value):
        return invoke_cli(self, self.cli_auth_params,
            ['variable', 'set', variable_id, value])

    def get_variable(self, variable_id):
        return invoke_cli(self, self.cli_auth_params,
            ['variable', 'get', variable_id])

    @integration_test
    def test_cli_can_set_and_get_a_defined_variable(self):
        expected_value='expected ' + uuid.uuid4().hex

        self.set_variable(CliIntegrationTest.DEFINED_VARIABLE_ID, expected_value)
        output = self.get_variable(CliIntegrationTest.DEFINED_VARIABLE_ID)

        self.assertEquals(expected_value, output)
