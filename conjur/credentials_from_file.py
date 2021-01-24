# -*- coding: utf-8 -*-

"""
CredentialsFromFile module

This module holds the logic for writing user-specific credentials
to a netrc file on the user's machine when they login
"""

# Builtins
import logging
import netrc
import os
import stat

# Internals
from conjur.constants import DEFAULT_NETRC_FILE
from conjur.credentials_data import CredentialsData

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
        if os.path.exists(self.netrc_path):
            netrc_obj = netrc.netrc(self.netrc_path)
            hosts = netrc_obj.hosts
            hosts[credential_data.machine] = (credential_data.login, None, credential_data.api_key)
            with open(DEFAULT_NETRC_FILE, "w") as netrc_file:
                ret = ""
                for i, entry in enumerate(str(netrc_obj).split('\n')):
                    if entry.strip().startswith('machine') and not i==0:
                        ret += '\n'
                    ret += entry + '\n'
                netrc_file.write(ret)
        else:
            with open(self.netrc_path, "w+") as netrc_file:
                netrc_file.write(f"machine {credential_data.machine}\n")
                netrc_file.write(f"login {credential_data.login}\n")
                netrc_file.write(f"password {credential_data.api_key}\n")

        # Ensures that the netrc file is only available its owner
        os.chmod(self.netrc_path, stat.S_IRWXU)

    def remove_credentials(self, conjurrc_appliance_url):
        """
        Method that removes netrc data from the file.
        Triggered during a logout
        """
        loaded_netrc = self.load(conjurrc_appliance_url)
        CredentialsData.remove_entry_from_file(loaded_netrc, DEFAULT_NETRC_FILE)

    def load(self, conjurrc_appliance_url):
        """
        Method that loads the netrc data.
        Triggered before each CLI action
        """
        # pylint: disable=logging-fstring-interpolation
        loaded_netrc = {}
        netrc_auth = ""
        netrc_obj = netrc.netrc(self.netrc_path)
        # For when the netrc exists but is empty. In the future
        # we might want to trigger the LOGIN command by creating
        # a custom error
        if netrc_obj.hosts == {}:
            raise Exception("Please log in")

        logging.debug(f"Retrieving credentials from file: {self.netrc_path}")
        for host in netrc_obj.hosts:
            if conjurrc_appliance_url in host:
                netrc_host_url = host
                netrc_auth = netrc_obj.authenticators(netrc_host_url)

        # The netrc_authn will be empty if the user already logged out
        # and attempts to logout again
        if netrc_auth == "":
            raise Exception("Please log in")

        login_id, _, api_key = netrc_auth
        loaded_netrc['machine'] = netrc_host_url
        loaded_netrc['api_key'] = api_key
        loaded_netrc['login_id'] = login_id

        return loaded_netrc
