# -*- coding: utf-8 -*-

"""
CredentialsFromFile module

This module holds the logic for writing user-specific credentials
to a netrc file on the user's machine when they login
"""

# Builtins
import logging
import os
import stat

# Internals
from conjur.constants import DEFAULT_NETRC_FILE

class CredentialsFromFile:
    """
    CredentialsFromFile

    This class holds logic when credentials are kept in the netrc
    """
    def __init__(self, netrc_path=DEFAULT_NETRC_FILE):
        self.netrc_path = netrc_path

    def save(self, credential_data):
        """
        Method that writes user data to a netrc file
        and updates permissions on the file
        """
        with open(self.netrc_path, 'w') as netrc_file:
            # pylint: disable=line-too-long
            netrc_file.write(f"""machine {credential_data.machine}
login {credential_data.login}
password {credential_data.api_key}
""")

        # Ensures that the netrc file is only available its owner
        os.chmod(self.netrc_path, stat.S_IRWXU)

    def remove_credentials(self):
        """
        Method that removes netrc data from the file.
        Triggered during a logout
        """
        open(self.netrc_path, "w").close()

    def load(self):
        """
        Method that loads the netrc data.
        Triggered before each CLI action
        """
        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Retrieving credentials from file: {self.netrc_path}")
        loaded_netrc = {}
        accum_netrc = []
        with open(self.netrc_path, 'r') as netrc_file:
            for line in netrc_file.readlines():
                key = line.split()
                accum_netrc.append(key[1])
        # pylint: disable=unbalanced-tuple-unpacking
        _, login_id, api_key = tuple(accum_netrc)

        loaded_netrc['api_key'] = api_key
        loaded_netrc['login_id'] = login_id

        return loaded_netrc
