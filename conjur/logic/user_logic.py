# -*- coding: utf-8 -*-

"""
UserLogic module

This module is the business logic for handling all user-related activity
"""

# Builtins
import logging
from typing import Tuple

# SDK
from conjur_sdk.interface.credentials_store_interface import CredentialsProviderInterface

# Internals
from conjur.errors import OperationNotCompletedException, HttpError

from conjur.resource import Resource
from conjur.data_object import ConjurrcData, CredentialsData


class UserLogic:
    """
    UserLogic

    This class holds the business logic for handling user activity
    """

    # TODO : Check Client type
    def __init__(self, conjurrc_data: ConjurrcData,
                 credential_provider: CredentialsProviderInterface, client):
        self.conjurrc_data = conjurrc_data
        self.credential_provider = credential_provider
        self.client = client

    # pylint: disable=logging-fstring-interpolation,line-too-long
    def rotate_api_key(self, resource_to_update: str) -> Tuple[str, str]:
        """
        Method to trigger two types of API key actions.
        1. The user can either rotate their own API key or
        2. Rotate another users API key
        """
        logged_in_credentials = self.extract_credentials_from_credential_store()
        logged_in_username = logged_in_credentials.login

        # if the user provides their own user id and they are logged in,
        # then for the sake of a successful outcome, we will ignore the input.
        # Otherwise, the Conjur server will fail the request.
        if resource_to_update in (None, logged_in_username):
            resource_to_update = logged_in_username
            new_api_key = self.rotate_personal_api_key(resource_to_update, logged_in_credentials,
                                                       logged_in_credentials.password)
        # the user supplied a user to rotate their API key
        else:
            new_api_key = self.rotate_other_api_key(resource_to_update)

        return resource_to_update, new_api_key

    # pylint: disable=logging-fstring-interpolation
    def change_personal_password(self, new_password: str) -> str:
        """
        Method to call the client to change the logged in user's password
        """
        logged_in_credentials = self.extract_credentials_from_credential_store()
        resource_to_update = logged_in_credentials.login
        logging.debug(f"Changing password for '{resource_to_update}'")
        # pylint: disable=line-too-long
        self.client.change_personal_password(resource_to_update, logged_in_credentials.password, new_password)
        return resource_to_update

    def extract_credentials_from_credential_store(self) -> CredentialsData:
        """
        Method to extract the login from the Credential Store.
        The login and password will later be used rotate API
        keys and change passwords
        """
        loaded_conjurrc = self.conjurrc_data.load_from_file()
        return self.credential_provider.load(loaded_conjurrc.conjur_url)

    def rotate_other_api_key(self, resource_to_update: str) -> str:
        """
        Method to make the call to rotate another user's API key
        """
        logging.debug(f"Rotating API key for '{resource_to_update}'...")

        resource = Resource(kind='user', identifier=resource_to_update)
        new_api_key = self.client.rotate_other_api_key(resource)
        logging.debug(f"Successfully rotated API key for '{resource_to_update}'")
        return new_api_key

    def rotate_personal_api_key(self, logged_in_username: str, logged_in_credentials: str,
                                current_password: str) -> str:
        """
        Method to call the client to rotate the logged-in user's personal API key
        """
        try:
            logging.debug(f"Rotating API key for '{logged_in_username}'...")
            new_api_key = self.client.rotate_personal_api_key(logged_in_username, current_password)

            # Update the new rotated API for the logged-in user
            logging.debug("Updating credential store with new API key "
                          f"for '{logged_in_username}'...")
            self.update_api_key_in_credential_store(logged_in_username,
                                                    logged_in_credentials,
                                                    new_api_key)
        except HttpError:
            raise
        except Exception as incomplete_operation:
            raise OperationNotCompletedException(str(incomplete_operation)) from incomplete_operation
        return new_api_key

    # pylint: disable=line-too-long
    def update_api_key_in_credential_store(self, resource_to_update: str, loaded_credentials: str, new_api_key: str):
        """
        Method to update the newly rotated API key in the credential store
        """
        self.credential_provider.update_api_key_entry(resource_to_update, loaded_credentials, new_api_key)
