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
            self.build_netrc(netrc_obj)
        else:
            with open(self.netrc_path, "w+") as netrc_file:
                netrc_file.write(f"machine {credential_data.machine}\n")
                netrc_file.write(f"login {credential_data.login}\n")
                netrc_file.write(f"password {credential_data.api_key}\n")

        # Ensures that the netrc file is only available its owner
        os.chmod(self.netrc_path, stat.S_IRWXU)

    def load(self, conjurrc_conjur_url):
        """
        Method that loads the netrc data.
        Triggered before each CLI action
        """
        # pylint: disable=logging-fstring-interpolation
        loaded_netrc = {}
        netrc_auth = ""
        netrc_obj = netrc.netrc(self.netrc_path)
        # For when the netrc exists but is completely empty. In the future
        # we might want to trigger the LOGIN command by creating
        # a custom error
        if netrc_obj.hosts == {}:
            raise Exception("You are already logged out")

        logging.debug(f"Retrieving credentials from file: {self.netrc_path}")
        for host in netrc_obj.hosts:
            if conjurrc_conjur_url in host:
                netrc_host_url = host
                netrc_auth = netrc_obj.authenticators(netrc_host_url)

        # The netrc_authn will be empty if the user already logged out
        # (their entry isn't found) and attempts to logout again
        if netrc_auth == "":
            raise Exception("You are already logged out")

        login_id, _, api_key = netrc_auth
        loaded_netrc['machine'] = netrc_host_url
        loaded_netrc['api_key'] = api_key
        loaded_netrc['login_id'] = login_id

        return loaded_netrc

    def update_api_key_entry(self, user_to_update, credential_data, new_api_key,
                             netrc_path=DEFAULT_NETRC_FILE):
        """
        Method to update the API key from the described entry in the netrc
        """
        netrc_obj = netrc.netrc(netrc_path)
        hosts = netrc_obj.hosts
        hosts[credential_data['machine']] = (user_to_update, None, new_api_key)
        self.build_netrc(netrc_obj)

    def remove_credentials(self, conjurrc_conjur_url):
        """
        Method that removes the described login entry from netrc
        """
        netrc_data = self.load(conjurrc_conjur_url)

        netrc_obj = netrc.netrc(DEFAULT_NETRC_FILE)
        hosts = netrc_obj.hosts
        hosts.pop(netrc_data['machine'], None)

        netrc_obj = netrc.netrc(DEFAULT_NETRC_FILE)
        netrc_obj.hosts.pop(netrc_data['machine'], None)
        self.build_netrc(netrc_obj)

    @classmethod
    def build_netrc(cls, netrc_obj):
        """
        Method to rewrite the netrc with contents from the netrc object
        """
        with open(DEFAULT_NETRC_FILE, 'w') as netrc_file:
            ret = ""
            for i, entry in enumerate(str(netrc_obj).split('\n')):
                if entry.strip().startswith('machine') and i != 0:
                    ret += '\n'
                ret += entry + '\n'

            netrc_file.write(ret.replace('\t', ''))
