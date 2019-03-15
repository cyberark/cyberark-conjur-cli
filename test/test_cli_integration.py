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
        set_params = self.cli_auth_params + \
            ["variable", "set", "one/password", "garbagevalue"]
        invoke_cli(self, set_params)

    @integration_test
    def test_cli_can_set_and_get_a_variable(self):
        expected_value='expected ' + uuid.uuid4().hex

        # Implicitly relies on the setter
        set_params = self.cli_auth_params + \
            ["variable", "set", "one/password", expected_value]
        invoke_cli(self, set_params)

        set_params = self.cli_auth_params + \
            ["variable", "get", "one/password"]
        output = invoke_cli(self, set_params)

        self.assertEquals(expected_value, output)
