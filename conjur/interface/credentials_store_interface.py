# -*- coding: utf-8 -*-

"""
CredentialsStoreInterface Interface

This class describes a shared interface for accessing user credentials
"""

# Internals
from conjur.data_object import CredentialsData

# pylint: disable=unnecessary-pass
class CredentialsStoreInterface: # pragma: no cover
    """
    CredentialsStoreInterface

    This class is an interface that outlines a shared interface for credential stores
    """
    def save(self, credential_data: CredentialsData):
        """
        Method that writes user data to a credential store
        """
        pass

    def load(self, conjurrc_conjur_url) -> CredentialsData:
        """
        Method that loads credentials
        """
        pass

    def update_api_key_entry(self, user_to_update, credential_data, new_api_key):
        """
        Method to update the API key from the described entry
        """
        pass

    def remove_credentials(self, conjurrc):
        """
        Method to remove credentials from a store
        """
        pass

    def is_exists(self, conjurrc_conjur_url) -> bool:
        """
        Method to check if credentials exist in a store
        """
        pass
