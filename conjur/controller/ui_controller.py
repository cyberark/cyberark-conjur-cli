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
from conjur.data_object.conjurrc_data import ConjurrcData
from conjur.logic.ui_logic import UiLogic, NotSupportedByServerException


class FileNotExistException(Exception):
    """
    Exception for when the user supplies a not complex enough password when
    attempting to change their password
    """


# pylint: disable=too-few-public-methods
class UIController:
    """
    LogoutController

    This class represents the Presentation Layer for the LOGOUT command
    """

    def __init__(self, ssl_verify: bool, ui_logic: UiLogic):
        self.ssl_verify = ssl_verify
        self.ui_logic = ui_logic

    def open_ui(self, open_as_window):
        """
        Method for removing credentials from user machine
        """

        self._validate_user_init_session()
        url = ConjurrcData.load_from_file().conjur_url
        try:
            if open_as_window:
                self.ui_logic.open_new_window(url)
            else:
                self.ui_logic.open_new_tab(url)
        except NotSupportedByServerException as not_supported_exception:
            raise Exception("UI is an Conjur Enterprise feature only")
        except Exception as err:
            raise Exception("Could not open Conjur UI") from err
        sys.stdout.write("Opened UI successfully\n")
        sys.stdout.flush()

    @staticmethod
    def _validate_user_init_session():
        try:
            conjur_data = ConjurrcData.load_from_file()
            if conjur_data.conjur_url is not None and len(conjur_data.conjur_url) > 0:
                return
        except FileNotExistException:
            pass
        raise Exception("Cli is not initialize. please 'conjur init' and try again")
