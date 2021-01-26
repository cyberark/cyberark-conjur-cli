# -*- coding: utf-8 -*-

"""
UserLogic module

This module is the business logic for handling all user-related activity
"""

# Builtins
import logging
import requests

# Internals
from conjur.credentials_from_file import CredentialsFromFile
from conjur.errors import InvalidOperationException, OperationNotCompletedSuccessfullyException


class UserLogic:
    """
    UserLogic

    This class holds the business logic for handling user activity
    """
    def __init__(self, conjurrc_data, credentials_from_store, client, resource):
        self.conjurrc_data=conjurrc_data
        self.credentials_from_store=credentials_from_store
        self.client=client
        self.resource=resource

    # pylint: disable=logging-fstring-interpolation,line-too-long
    def rotate_api_key(self, resource_to_update):
        """
        Method to trigger two types of API key actions.
        1. The user can either rotate their own API key or
        2. Rotate another users API key
        """
        loaded_credentials = self.extract_credentials_from_credential_store()
        user_from_credential_store = loaded_credentials['login_id']
        if resource_to_update == user_from_credential_store:
            raise InvalidOperationException("To rotate the API key of the currently logged-in user "\
                                   "use this command without any flags or options")
        if resource_to_update is not None:
            user_from_credential_store = resource_to_update
            logging.debug(f"Rotating API key for '{user_from_credential_store}'")

            new_api_key = self.rotate_other_api_key(user_from_credential_store)
            logging.debug(f"Successfully rotated API key for '{user_from_credential_store}'")
        else:
            # if the user does not provide a user to rotate their API key,
            # their own API key will be rotated
            try:
                logging.debug(f"Rotating API key for '{user_from_credential_store}'")
                new_api_key = self.rotate_personal_api_key(user_from_credential_store,
                                                           loaded_credentials['api_key'])

                # Update the new rotated API for the logged-in user
                logging.debug("Updating credential store with new API key " \
                              f"for '{user_from_credential_store}'")
                self.update_api_key_in_credential_store(user_from_credential_store,
                                                        loaded_credentials,
                                                        new_api_key)
            except requests.exceptions.HTTPError:
                raise
            except Exception as incomplete_operation:
                raise OperationNotCompletedSuccessfullyException from incomplete_operation

        return user_from_credential_store, new_api_key

    # pylint: disable=logging-fstring-interpolation
    def change_personal_password(self, new_password):
        """
        Method to call the client to change the logged in user's password
        """
        loaded_credentials = self.extract_credentials_from_credential_store()
        resource_to_update = loaded_credentials['login_id']
        logging.debug(f"Changing password for '{resource_to_update}'")
        # pylint: disable=line-too-long
        return resource_to_update, self.client.change_personal_password(self.resource, resource_to_update, loaded_credentials['api_key'], new_password)

    def extract_credentials_from_credential_store(self):
        """
        Method to extract the login from the Credential Store.
        The login and password will later be used rotate API
        keys and change passwords
        """
        loaded_conjurrc = self.conjurrc_data.load_from_file()
        return self.credentials_from_store.load(loaded_conjurrc.appliance_url)

    def rotate_other_api_key(self, resource_to_rotate):
        """
        Method to make the call to rotate another user's API key
        """
        return self.client.rotate_other_api_key(self.resource, resource_to_rotate)

    def rotate_personal_api_key(self, logged_in_user, current_password):
        """
        Method to call the client to rotate the logged-in user's personal API key
        """
        return self.client.rotate_personal_api_key(self.resource, logged_in_user, current_password)

    @classmethod
    # pylint: disable=line-too-long
    def update_api_key_in_credential_store(cls, resource_to_update, loaded_credentials, new_api_key):
        """
        Method to update the newly rotated API key in the credential store
        """
        credentials = CredentialsFromFile()
        credentials.update_api_key_entry(resource_to_update, loaded_credentials, new_api_key)
