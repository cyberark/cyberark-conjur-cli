import os
import uuid
from unittest.mock import patch


def remove_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)

@patch('builtins.input', return_value='yes')
def init_to_cli(self, mock_input):
    self.invoke_cli(self.cli_auth_params,
                    ['init', '-u', self.client_params.hostname, '-a', self.client_params.account], exit_code=0)

def login_to_cli(self):
    self.invoke_cli(self.cli_auth_params,
            ['login', '-n', self.client_params.login, '-p', self.client_params.env_api_key], exit_code=0)

def setup_cli(self):
    init_to_cli(self)
    login_to_cli(self)

 # *************** VARIABLE ***************

def set_variable(self, variable_id, value, exit_code=0):
    return self.invoke_cli(self.cli_auth_params,
                       ['variable', 'set', '-i', variable_id, '-v', value], exit_code=exit_code)

def get_variable(self, *variable_ids):
    return self.invoke_cli(self.cli_auth_params,
                           ['variable', 'get', '-i', *variable_ids])

def assert_set_and_get(self, variable_id):
    expected_value = uuid.uuid4().hex

    set_variable(self, variable_id, expected_value)
    output = get_variable(self, variable_id)
    self.assertEquals(expected_value, output.strip())

 # *************** POLICY ***************

def apply_policy(self, policy_path):
    return self.invoke_cli(self.cli_auth_params,
                           ['policy', 'apply', 'root', policy_path])

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
