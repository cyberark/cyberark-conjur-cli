# -*- coding: utf-8 -*-

"""
CredentialsData module

This module represents an object that holds netrc data
"""
# Builtins
import netrc

# Internals
from conjur.constants import DEFAULT_NETRC_FILE

# pylint: disable=too-few-public-methods
class CredentialsData:
    """
    Used for setting user input data to login to Conjur
    """

    def __init__(self, machine=None, login=None, password=None):
        self.machine = machine
        self.login = login

        # .netrc file format standard uses password but this value
        # is actually the user/host api key. This convention should be kept.
        # See https://www.labkey.org/Documentation/wiki-page.view?name=netrc
        # especially the 'Use API Keys' section
        self.api_key = password

    @classmethod
    def remove_entry_from_file(cls, netrc_data, netrc_path):
        """
        Method that removes the described login entry from netrc
        """
        netrc_obj = netrc.netrc(netrc_path)
        hosts = netrc_obj.hosts
        hosts.pop(netrc_data['machine'], None)

        netrc_obj = netrc.netrc(netrc_path)
        netrc_obj.hosts.pop(netrc_data['machine'], None)
        cls.build_netrc_from_instance(netrc_obj)

    @classmethod
    def build_netrc_from_instance(cls, netrc_obj):
        """
        Method to write to the netrc with contents from the netrc object
        """
        with open(DEFAULT_NETRC_FILE, 'w') as netrc_file:
            ret = ""
            for i, entry in enumerate(str(netrc_obj).split('\n')):
                if entry.strip().startswith('machine') and i != 0:
                    ret += '\n'
                ret += entry + '\n'

            netrc_file.write(ret.replace('\t' ,''))

    @classmethod
    def update_api_key_entry(cls, user_to_update, credential_data, new_api_key,
                             netrc_path=DEFAULT_NETRC_FILE):
        """
        Method to update the API key from the described entry in the netrc
        """
        netrc_obj = netrc.netrc(netrc_path)
        hosts = netrc_obj.hosts
        hosts[credential_data['machine']] = (user_to_update, None, new_api_key)
        cls.build_netrc_from_instance(netrc_obj)

    # pylint: disable=line-too-long
    def __repr__(self):
        return f"{{'machine': {self.machine}, 'login': {self.login}, 'password': ****}}"
