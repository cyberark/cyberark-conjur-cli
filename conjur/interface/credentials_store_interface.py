# -*- coding: utf-8 -*-

"""
CredentialsStoreInterface Interface
This class describes a shared interface for accessing user credentials
"""

# Builtins
import abc

# Internals
from conjur.data_object import CredentialsData, ConjurrcData


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
    def load(self, conjurrc_conjur_url: str) -> CredentialsData:
        """
        Method that loads credentials
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def update_api_key_entry(self, user_to_update: str,
                             credential_data: CredentialsData, new_api_key: str):
        """
        Method to update the API key from the described entry
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def remove_credentials(self, conjurrc: ConjurrcData):
        """
        Method to remove credentials from a store
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def is_exists(self, conjurrc_conjur_url: str) -> bool:
        """
        Method to check if credentials exist in a store
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def cleanup_if_exists(self, conjurrc_conjur_url: str):
        """
        Method to cleanup credential leftovers if exist.
        For example, if a user delete item manually from the local pc keyring,
        this function will make sure no leftovers left.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def get_store_location(self):
        """
        Method to return the source of the credentials
        """
        raise NotImplementedError()
