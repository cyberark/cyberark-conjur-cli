# -*- coding: utf-8 -*-

"""
LogoutController module

This module is the controller that facilitates all logout actions
required to successfully logout
"""

# Internals
from conjur.constants import DEFAULT_CONFIG_FILE
from conjur.data_object.conjurrc_data import ConjurrcData
from conjur.interface.credentials_store_interface import CredentialsStoreInterface

# pylint: disable=too-few-public-methods
class LogoutController:
    """
    LogoutController

    This class represents the Presentation Layer for the LOGOUT command
    """
    def __init__(self, ssl_verify:bool, logout_logic, credentials_provider: CredentialsStoreInterface):
        self.ssl_verify = ssl_verify
        self.logout_logic = logout_logic
        self.credentials_provider = credentials_provider

    def remove_credentials(self):
        """
        Method for removing credentials from user machine
        """
        try:
            loaded_conjurrc = ConjurrcData.load_from_file(DEFAULT_CONFIG_FILE)
            if not self.credentials_provider.is_exists(loaded_conjurrc.conjur_url):
                # Cleans up credentials leftover to make sure the environment is
                # not left in a partial state. For example, if user deleted
                # their username or password manually.
                self.logout_logic.cleanup_credentials(loaded_conjurrc)
                raise Exception("You are already logged out.")
            self.logout_logic.remove_credentials(loaded_conjurrc)
        except Exception as error:
            # pylint: disable=raise-missing-from
            raise Exception(f"Failed to log out. {error}")
