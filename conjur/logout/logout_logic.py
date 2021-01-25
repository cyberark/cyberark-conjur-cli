# -*- coding: utf-8 -*-

"""
LogoutLogic module

This module is the business logic for logging out of the Conjur CLI
"""
# pylint: disable=too-few-public-methods
class LogoutLogic:
    """
    LogoutLogic

    This class holds the business logic for logging out of Conjur
    """
    credentials = None

    def __init__(self, credentials):
        self.credentials = credentials

    def remove_credentials(self, conjurrc_appliance_url):
        """
        Method to remove credentials during logout
        """
        self.credentials.remove_credentials(conjurrc_appliance_url)
