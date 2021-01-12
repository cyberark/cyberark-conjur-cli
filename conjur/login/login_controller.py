# -*- coding: utf-8 -*-

"""
LoginController module

This module is the controller that facilitates all login actions
required to successfully configure the Credentials
"""

# Builtins
import getpass
import logging
import sys

from Utils.utils import Utils
from conjur.constants import CREDENTIAL_HOST_PATH, DEFAULT_NETRC_FILE
from conjur.init import ConjurrcData

class LoginController:
    """
    LoginController

    This class represents the Presentation Layer for the LOGIN command
    """

    def __init__(self, ssl_verify, user_password, credential_data, login_logic):
        self.ssl_verify = ssl_verify
        if self.ssl_verify is False:
            Utils.get_insecure_warning()

        self.user_password = user_password
        self.credential_data = credential_data
        self.login_logic = login_logic

    def load(self):
        """
        Method that facilitates all method calls in this class
        """
        self.get_username()
        self.get_password()

        conjurrc = self.load_conjurrc_data()
        self.get_api_key(conjurrc)

        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Saving credentials to '{DEFAULT_NETRC_FILE}'")
        self.login_logic.save(self.credential_data)
        # pylint: disable=logging-fstring-interpolation
        logging.debug("Credentials written to " \
                      f"'{DEFAULT_NETRC_FILE}'")
        sys.stdout.write("Successfully logged in to Conjur\n")

    def get_username(self):
        """
        Method to fetch the username if the user did not provide one
        """
        if self.credential_data.login is None:
            # pylint: disable=logging-fstring-interpolation,line-too-long
            self.credential_data.login = input("To log in to Conjur, enter your login name: ").strip()
            if self.credential_data.login == '':
                # pylint: disable=raise-missing-from
                raise RuntimeError("Error: Login name is required")

    def get_password(self):
        """
        Method to fetch the password from the user attempting to login
        """
        if self.user_password is None:
            # pylint: disable=line-too-long
            self.user_password = getpass.getpass(prompt=f"Please enter {self.credential_data.login}'s password (it will not be echoed): ")
            while self.user_password == '':
                self.user_password = getpass.getpass(prompt=f"Invalid format. Please enter {self.credential_data.login}'s password (it will not be echoed): ")

    def load_conjurrc_data(self):
        """
        Method to load the conjurrc data because it is needed to fill in netrc
        properties and to send a login request to Conjur
        """
        conjurrc = ConjurrcData.load_from_file()
        self.credential_data.machine = conjurrc.appliance_url + CREDENTIAL_HOST_PATH

        return conjurrc

    def get_api_key(self, conjurrc):
        """
        Method to fetch the user/host's API key from Conjur which is to be added to the netrc
        """
        try:
            self.credential_data.api_key = self.login_logic.get_api_key(self.ssl_verify,
                                                           self.credential_data,
                                                           self.user_password,
                                                           conjurrc)
        except Exception as error:
            raise RuntimeError("Failed to log in to Conjur. Unable to authenticate with Conjur. " \
                f"Reason: {error}.") from error
