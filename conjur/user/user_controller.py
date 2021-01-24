# -*- coding: utf-8 -*-

"""
UserController module

This module is the controller that facilitates all user actions
"""

# Builtins
import getpass
import logging
import sys
import requests

class UserController():
    """
    UserController

    This class represents the Presentation Layer for the User command.
    """
    def __init__(self, user_logic, user_resource_data):
        self.user_logic=user_logic
        self.user_resource_data=user_resource_data

    def rotate_api_key(self):
        """
        Method that calls to rotate api key logic to perform the rotation
        """
        # pylint: disable=line-too-long
        resource_to_update, new_api_key = self.user_logic.rotate_api_key(self.user_resource_data.user_id)
        sys.stdout.write(f"API key for '{resource_to_update}' was successfully rotated. " \
                         f"New API key is: {new_api_key}\n")

    # pylint: disable=logging-fstring-interpolation,line-too-long
    def change_password(self):
        """
        Method that calls to change password to perform the change
        """
        self.prompt_for_password()
        try:
            self.user_logic.change_password(self.user_resource_data.new_password)
        except requests.exceptions.HTTPError as http_error:
            logging.debug("Invalid password. Please verify that it has the correct password complexity")

            raise requests.exceptions.HTTPError("Invalid password. Please verify that " \
                                                "it has the correct password complexity") from http_error
        logging.debug("Password successfully changed")
        sys.stdout.write('Password has been successfully changed\n')

    def prompt_for_password(self):
        """
        Method to prompt user for the password if they did not provide one
        """
        if self.user_resource_data.new_password is None:
            # pylint: disable=line-too-long
            self.user_resource_data.new_password = getpass.getpass(prompt="Please enter the new password (it will not be echoed): ")
            while self.user_resource_data.new_password == '':
                self.user_resource_data.new_password = getpass.getpass(prompt="Invalid format. Please enter " \
                                                                              "the new password (it will not be echoed): ")
