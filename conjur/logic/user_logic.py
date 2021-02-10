# -*- coding: utf-8 -*-

"""
UserLogic module

This module is the business logic for handling all user-related activity
"""

# Builtins
import logging
import requests

# Internals
from conjur.errors import OperationNotCompletedException
from conjur.util.credentials_from_file import CredentialsFromFile
from conjur.resource import Resource


class UserLogic:
    """
    UserLogic

    This class holds the business logic for handling user activity
    """
    def __init__(self, conjurrc_data, credentials_from_store, client):
        self.conjurrc_data=conjurrc_data
        self.credentials_from_store=credentials_from_store
        self.client=client

    # pylint: disable=logging-fstring-interpolation,line-too-long
    def rotate_api_key(self, resource_to_update):
        """
        Method to trigger two types of API key actions.
        1. The user can either rotate their own API key or
        2. Rotate another users API key
        """
        logged_in_credentials = self.extract_credentials_from_credential_store()
        logged_in_username = logged_in_credentials['login_id']

        # if the user provides their own user id and they are logged in,
        # then for the sake of a successful outcome, we will ignore the input.
        # Otherwise, the Conjur server will fail the request.
        if resource_to_update in (None, logged_in_username):
            resource_to_update = logged_in_username
            new_api_key = self.rotate_personal_api_key(resource_to_update, logged_in_credentials, logged_in_credentials['api_key'])
        # the user supplied a user to rotate their API key
        else:
            new_api_key = self.rotate_other_api_key(resource_to_update)

        return resource_to_update, new_api_key

    # pylint: disable=logging-fstring-interpolation
    def change_personal_password(self, new_password):
        """
        Method to call the client to change the logged in user's password
        """
        logged_in_credentials = self.extract_credentials_from_credential_store()
        resource_to_update = logged_in_credentials['login_id']
        logging.debug(f"Changing password for '{resource_to_update}'")
        # pylint: disable=line-too-long
        return resource_to_update, self.client.change_personal_password(resource_to_update, logged_in_credentials['api_key'], new_password)

    def extract_credentials_from_credential_store(self):
        """
        Method to extract the login from the Credential Store.
        The login and password will later be used rotate API
        keys and change passwords
        """
        loaded_conjurrc = self.conjurrc_data.load_from_file()
        return self.credentials_from_store.load(loaded_conjurrc.appliance_url)

    def rotate_other_api_key(self, resource_to_update):
        """
        Method to make the call to rotate another user's API key
        """
        logging.debug(f"Rotating API key for '{resource_to_update}'")

        resource = Resource(type_='user', name=resource_to_update)
        new_api_key = self.client.rotate_other_api_key(resource)
        logging.debug(f"Successfully rotated API key for '{resource_to_update}'")
        return new_api_key

    def rotate_personal_api_key(self, logged_in_username, logged_in_credentials, current_password):
        """
        Method to call the client to rotate the logged-in user's personal API key
        """
        try:
            logging.debug(f"Rotating API key for '{logged_in_username}'")
            new_api_key = self.client.rotate_personal_api_key(logged_in_username, current_password)

            # Update the new rotated API for the logged-in user
            logging.debug("Updating credential store with new API key "
                          f"for '{logged_in_username}'")
            self.update_api_key_in_credential_store(logged_in_username,
                                                    logged_in_credentials,
                                                    new_api_key)
        except requests.exceptions.HTTPError:
            raise
        except Exception as incomplete_operation:
            raise OperationNotCompletedException from incomplete_operation
        return new_api_key

    @classmethod
    # pylint: disable=line-too-long
    def update_api_key_in_credential_store(cls, resource_to_update, loaded_credentials, new_api_key):
        """
        Method to update the newly rotated API key in the credential store
        """
        credentials = CredentialsFromFile()
        credentials.update_api_key_entry(resource_to_update, loaded_credentials, new_api_key)
