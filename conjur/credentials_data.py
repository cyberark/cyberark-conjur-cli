# -*- coding: utf-8 -*-

"""
CredentialsData module

This module represents an object that holds netrc data
"""

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

    @staticmethod
    def remove_entry_from_file(netrc_data, netrc_path):
        """
        Method that removes the described login entry from netrc
        """
        # pylint: disable=import-outside-toplevel
        import netrc

        netrc_obj = netrc.netrc(netrc_path)
        hosts = netrc_obj.hosts
        hosts.pop(netrc_data['machine'], None)

        netrc_obj = netrc.netrc(netrc_path)
        netrc_obj.hosts.pop(netrc_data['machine'], None)
        with open(DEFAULT_NETRC_FILE, 'w') as netrc_file:
            ret = ""
            for i, entry in enumerate(str(netrc_obj).split('\n')):
                if entry.strip().startswith('machine') and i != 0:
                    ret += '\n'
                ret += entry + '\n'

            netrc_file.write(ret.replace('\t' ,''))

    # pylint: disable=line-too-long
    def __repr__(self):
        return "{'machine': %r, 'login': %r, 'password': ****}" % (self.machine,
                                                                   self.login)
