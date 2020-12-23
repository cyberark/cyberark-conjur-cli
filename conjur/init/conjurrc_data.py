# -*- coding: utf-8 -*-

"""
ConjurrcData module

This module represents an object that holds conjurrc data
"""
# pylint: disable=too-few-public-methods
class ConjurrcData:
    """
    Used for setting user input data
    """
    def __init__(self, appliance_url = None, account = None, cert_file = None):
        self.appliance_url = appliance_url
        self.account = account
        self.cert_file = cert_file
        self.plugins = []

    # pylint: disable=line-too-long
    def __repr__(self):
        return "{'appliance_url': %r, 'account': %r, 'cert_file': %r, 'plugins': %r}" % (self.appliance_url,
                                                                                         self.account,
                                                                                         self.cert_file,
                                                                                         self.plugins)
