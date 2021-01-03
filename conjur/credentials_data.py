# -*- coding: utf-8 -*-

"""
CredentialsData module

This module represents an object that holds netrc data
"""

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

    # pylint: disable=line-too-long
    def __repr__(self):
        return "{'machine': %r, 'login': %r, 'password': ****}" % (self.machine,
                                                                   self.login)
