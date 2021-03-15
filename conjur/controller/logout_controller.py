# -*- coding: utf-8 -*-

"""
LogoutController module

This module is the controller that facilitates all logout actions
required to successfully logout
"""

# Builtins
import logging

# Third party
import keyring

# Internals
from conjur.constants import DEFAULT_CONFIG_FILE
from conjur.data_object.conjurrc_data import ConjurrcData

# pylint: disable=too-few-public-methods
class LogoutController:
    """
    LogoutController

    This class represents the Presentation Layer for the LOGOUT command
    """
    def __init__(self, ssl_verify, logout_logic):
        self.ssl_verify = ssl_verify
        self.logout_logic = logout_logic

    def remove_credentials(self):
        """
        Method for removing credentials from user machine
        """
        try:
            loaded_conjurrc = ConjurrcData.load_from_file(DEFAULT_CONFIG_FILE)
            self.logout_logic.remove_credentials(loaded_conjurrc)
        # Catches when credentials do not exist in the keyring. If the key does not exist,
        # the user has already logged out
        except keyring.errors.PasswordDeleteError:
            # pylint: disable=logging-fstring-interpolation
            logging.debug("Successfully removed credentials from the "
                          f"keyring '{keyring.get_keyring().name}'")
            return
        except keyring.errors.KeyringError:
            raise
        except Exception as error:
            # pylint: disable=raise-missing-from
            raise Exception(f"Failed to log out. {error}")
