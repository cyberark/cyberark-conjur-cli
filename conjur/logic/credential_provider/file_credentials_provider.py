# -*- coding: utf-8 -*-

"""
FileCredentialsProvider module

This module holds the logic for writing user-specific credentials
to a netrc file on the user's machine when they login
"""

# Builtins
import logging
import netrc
import os
import stat

# Internals
from conjur.constants import DEFAULT_NETRC_FILE, MACHINE, PASSWORD, LOGIN
from conjur.data_object import CredentialsData
from conjur.errors import CredentialRetrievalException
from conjur.interface.credentials_store_interface import CredentialsStoreInterface

# pylint: disable=logging-fstring-interpolation, line-too-long
class FileCredentialsProvider(CredentialsStoreInterface):
    """
    FileCredentialsProvider

    This class holds logic when credentials are kept in the netrc
    """

    def __init__(self, netrc_path=DEFAULT_NETRC_FILE):
        self.netrc_path = netrc_path

    def save(self, credential_data):
        """
        Method that writes user data to a netrc file
        and updates permissions on the file
        """
        logging.warning("No supported keystore found! Saving credentials in "
                        f"plaintext in '{DEFAULT_NETRC_FILE}'. Make sure to logoff "
                        "after you have finished using the CLI")
        logging.debug(f"Attempting to write credentials to '{DEFAULT_NETRC_FILE}'...")
        # TDOO use private function
        if os.path.exists(self.netrc_path):
            netrc_obj = netrc.netrc(self.netrc_path)
            hosts = netrc_obj.hosts
            hosts[credential_data.machine] = (credential_data.login, None, credential_data.password)
            self.build_netrc(netrc_obj)
        else:
            with open(self.netrc_path, "w+") as netrc_file:
                netrc_file.write(f"machine {credential_data.machine}\n")
                netrc_file.write(f"login {credential_data.login}\n")
                netrc_file.write(f"password {credential_data.password}\n")

        # Ensures that the netrc file is only available its owner
        os.chmod(self.netrc_path, stat.S_IRWXU)
        logging.debug(f"Credentials written to '{DEFAULT_NETRC_FILE}'")

    def load(self, conjurrc_conjur_url):
        """
        Method that loads the netrc data.
        Triggered before each CLI action
        """
        try:
            if not self.is_exists(conjurrc_conjur_url):
                raise CredentialRetrievalException
            # TODO use private function
            loaded_credentials = {}
            netrc_auth = ""
            netrc_obj = netrc.netrc(self.netrc_path)

            logging.debug(f"Retrieving credentials from file '{self.netrc_path}'...")
            for host in netrc_obj.hosts:
                if conjurrc_conjur_url in host:
                    netrc_host_url = host
                    netrc_auth = netrc_obj.authenticators(netrc_host_url)

            login, _, password = netrc_auth
            loaded_credentials[MACHINE] = netrc_host_url
            loaded_credentials[PASSWORD] = password
            loaded_credentials[LOGIN] = login
            return CredentialsData.convert_dict_to_obj(loaded_credentials)
        except netrc.NetrcParseError as netrc_error:
            raise Exception("Error: netrc is in an invalid format. "
                            f"Reason: {netrc_error}") from netrc_error

    def is_exists(self, conjurrc_conjur_url) -> bool:
        if not os.path.exists(DEFAULT_NETRC_FILE) or os.path.getsize(DEFAULT_NETRC_FILE) == 0:
            return False

        netrc_auth = ""
        netrc_obj = netrc.netrc(self.netrc_path)
        # For when the netrc exists but is completely empty. In the future
        # we might want to trigger the LOGIN command by creating
        # a custom error
        if netrc_obj.hosts == {}:
            return False

        for host in netrc_obj.hosts:
            if conjurrc_conjur_url in host:
                netrc_host_url = host
                netrc_auth = netrc_obj.authenticators(netrc_host_url)

        # The netrc_authn will be empty if the user already logged out
        # (their entry isn't found) and attempts to logout again
        if netrc_auth == "":
            return False

        return True

    def update_api_key_entry(self, user_to_update, credential_data, new_api_key):
        """
        Method to update the API key from the described entry in the netrc
        """
        netrc_obj = netrc.netrc(DEFAULT_NETRC_FILE)
        hosts = netrc_obj.hosts
        hosts[credential_data.machine] = (user_to_update, None, new_api_key)
        self.build_netrc(netrc_obj)

    def remove_credentials(self, conjurrc):
        """
        Method that removes the described login entry from netrc
        """
        logging.debug(f"Attempting to remove credentials from '{DEFAULT_NETRC_FILE}'...")
        # pylint: disable=no-else-return
        if not os.path.exists(DEFAULT_NETRC_FILE):
            return
        elif os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0:
            credential_data = self.load(conjurrc.conjur_url)

            netrc_obj = netrc.netrc(DEFAULT_NETRC_FILE)
            hosts = netrc_obj.hosts
            hosts.pop(credential_data.machine, None)

            netrc_obj = netrc.netrc(DEFAULT_NETRC_FILE)
            netrc_obj.hosts.pop(credential_data.machine, None)
            self.build_netrc(netrc_obj)
        else:
            raise Exception("You are already logged out.")

        logging.debug(f"Successfully removed credentials from '{DEFAULT_NETRC_FILE}'")

    # TODO check if we are using outside of this class. if not make private
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
