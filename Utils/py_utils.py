import os
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
