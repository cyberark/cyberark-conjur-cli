# -*- coding: utf-8 -*-

"""
CredentialsStoreInterface Interface

This class describes a shared interface for accessing user credentials
"""

# Builtins
import abc

# Internals
from conjur.data_object import CredentialsData


class CredentialsStoreInterface(metaclass=abc.ABCMeta):  # pragma: no cover
    """
    CredentialsStoreInterface

    This class is an interface that outlines a shared interface for credential stores
    """

    @abc.abstractmethod
    def save(self, credential_data: CredentialsData):
        """
        Method that writes user data to a credential store
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def load(self, conjurrc_conjur_url) -> CredentialsData:
        """
        Method that loads credentials
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def update_api_key_entry(self, user_to_update, credential_data, new_api_key):
        """
        Method to update the API key from the described entry
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def remove_credentials(self, conjurrc):
        """
        Method to remove credentials from a store
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def is_exists(self, conjurrc_conjur_url) -> bool:
        """
        Method to check if credentials exist in a store
        """
        raise NotImplementedError()
