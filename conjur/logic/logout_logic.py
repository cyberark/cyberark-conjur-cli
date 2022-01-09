# -*- coding: utf-8 -*-

"""
LogoutLogic module

This module is the business logic for logging out of the Conjur CLI
"""
# SDK
from conjur_sdk.interface.credentials_store_interface import CredentialsProviderInterface
# Internals
from conjur.data_object import ConjurrcData


# pylint: disable=too-few-public-methods
class LogoutLogic:
    """
    LogoutLogic

    This class holds the business logic for logging out of Conjur
    """

    def __init__(self, credentials_provider: CredentialsProviderInterface):
        self.credentials_provider = credentials_provider

    def remove_credentials(self, conjurrc: ConjurrcData):
        """
        Method to remove credentials during logout
        """
        self.credentials_provider.remove_credentials(conjurrc)

    def cleanup_credentials(self, conjurrc: ConjurrcData):
        """
        Method to remove credentials during logout
        """
        self.credentials_provider.cleanup_if_exists(conjurrc.conjur_url)
