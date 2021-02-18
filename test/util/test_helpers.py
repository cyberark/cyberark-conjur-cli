import os
import signal
import tempfile
import uuid
from unittest.mock import patch

# *************************************************
# *********** INTEGRATION TESTS HELPERS ***********
# *************************************************
from conjur.constants import DEFAULT_CONFIG_FILE


def remove_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)

def run_func_with_timeout(timeout, func,*args):
    # IMPORTANT! this must raise an exception for the interrupt to work with blocking functions
    def interrupted(signum, frame):
        raise RuntimeError("interrupted")
    signal.signal(signal.SIGALRM, interrupted)
    # set alarm
    signal.alarm(timeout)
    function_output = func(*args)
    # disable the alarm after success
    signal.alarm(0)
    return function_output

@patch('builtins.input', return_value='yes')
def init_to_cli(self, mock_input):
    self.invoke_cli(self.cli_auth_params,
                    ['init', '-u', self.client_params.hostname, '-a', self.client_params.account])

def login_to_cli(self):
    self.invoke_cli(self.cli_auth_params,
            ['login', '-i', self.client_params.login, '-p', self.client_params.env_api_key])

def setup_cli(self):
    init_to_cli(self)
    login_to_cli(self)

 # *************** INIT ***************

def verify_conjurrc_contents(account, hostname, cert):
    with open(f"{DEFAULT_CONFIG_FILE}", 'r') as conjurrc:
        lines = conjurrc.readlines()
        assert "---" in lines[0]
        assert f"account: {account}" in lines[1]
        assert f"appliance_url: {hostname}" in lines[2]
        assert f"cert_file: {cert}" in lines[3]
        assert f"plugins: []" in lines[4]

 # *************** VARIABLE ***************

def set_variable(self, variable_id, value, exit_code=0):
    return self.invoke_cli(self.cli_auth_params,
                       ['variable', 'set', '-i', variable_id, '-v', value], exit_code=exit_code)

def get_variable(self, *variable_ids, exit_code=0):
    return self.invoke_cli(self.cli_auth_params,
                           ['variable', 'get', '-i', *variable_ids], exit_code=exit_code)

def assert_set_and_get(self, variable_id):
    expected_value = uuid.uuid4().hex

    set_variable(self, variable_id, expected_value)
    output = get_variable(self, variable_id)
    # using AssertIn and not AssertEqual as in the process we get the entire Conjur STDOUT stdout
    self.assertIn(expected_value, output.strip())


def assert_variable_set_fails(self, variable_id, error_class, exit_code=0):
    with self.assertRaises(error_class):
        self.set_variable(variable_id, uuid.uuid4().hex, exit_code)

def print_instead_of_raise_error(self, variable_id, error_message_regex):
    output = self.invoke_cli(self.cli_auth_params,
                             ['variable', 'set', '-i', variable_id, '-v', uuid.uuid4().hex], exit_code=1)

    self.assertRegex(output, error_message_regex)

 # *************** POLICY ***************

def generate_policy_string(self):
        variable_1 = 'simple/basic/{}'.format(uuid.uuid4().hex)
        variable_2 = 'simple/space filled/{}'.format(uuid.uuid4().hex)
        variable_3 = 'simple/special @#$%^&*(){{}}[]._+/{id}'.format(id=uuid.uuid4().hex)

# this policy is purposefully not indented because
# the """ formatter is indentation sensitive and
# policy should start at the far left of the line
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

def load_policy(self, policy_path, exit_code=0):
    return self.invoke_cli(self.cli_auth_params,
                           ['policy', 'load', '-b', 'root', '-f', policy_path], exit_code=exit_code)

def load_policy_from_string(self, policy, exit_code=0):
    file_name = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
    with open(file_name, 'w+b') as temp_policy_file:
        temp_policy_file.write(policy.encode('utf-8'))
        temp_policy_file.flush()
        output = load_policy(self, temp_policy_file.name, exit_code)

    os.remove(file_name)
    return output

def replace_policy(self, policy_path, exit_code=0):
    return self.invoke_cli(self.cli_auth_params,
                           ['policy', 'replace', '-b', 'root', '-f', policy_path], exit_code=exit_code)

def replace_policy_from_string(self, policy, exit_code=0):
    output = None
    file_name = os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
    with open(file_name, 'w+b') as temp_policy_file:
        temp_policy_file.write(policy.encode('utf-8'))
        temp_policy_file.flush()

        # Run the new replace that should not result in newly created roles
        output = replace_policy(self, temp_policy_file.name, exit_code)

    os.remove(file_name)
    return output

def update_policy(self, policy_path):
    return self.invoke_cli(self.cli_auth_params,
                           ['policy', 'update', '-b', 'root', '-f', policy_path])

def update_policy_from_string(self, policy):
    output = None
    file_name=os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
    with open(file_name, 'w+b') as temp_policy_file:
        temp_policy_file.write(policy.encode('utf-8'))
        temp_policy_file.flush()

        # Run the new update that should not result in newly created roles
        output = update_policy(self, temp_policy_file.name)
    os.remove(file_name)
    return output

# *************************************************
# *************** UNIT TESTS HELPERS **************
# *************************************************

def validate_netrc_contents(self):
    with open('path/to/netrc', 'r') as netrc:
        lines = netrc.readlines()
        self.assertEquals(lines[0].strip(), "machine https://someurl/authn")
        self.assertEquals(lines[1].strip(), "login somelogin")
        self.assertEquals(lines[2].strip(), "password somepass")
