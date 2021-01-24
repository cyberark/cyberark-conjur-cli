# -*- coding: utf-8 -*-

"""
LogoutController module

This module is the controller that facilitates all logout actions
required to successfully logout
"""

# Builtins
import logging
import os
import sys

# Internals
from conjur.constants import DEFAULT_NETRC_FILE, DEFAULT_CONFIG_FILE
from conjur.init import ConjurrcData

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
        logging.debug("Attempting to log out of Conjur")
        try:
            if os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0:
                conjurrc = ConjurrcData.load_from_file(DEFAULT_CONFIG_FILE)
                self.logout_logic.remove(conjurrc.appliance_url)
                logging.debug("Logout successful")
                sys.stdout.write("Logged out of Conjur\n")
            else:
                raise Exception("Please log in")
        except Exception as error:
            # pylint: disable=raise-missing-from
            raise Exception(f"Failed to log out. {error}.")
