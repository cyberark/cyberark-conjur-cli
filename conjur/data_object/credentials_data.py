# -*- coding: utf-8 -*-

"""
CredentialsData module

This module represents the DTO that holds credential data
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
        return f"{{'machine': '{self.machine}', 'login': '{self.login}', 'password': '****'}}"
