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

# Internals
from conjur.errors import InvalidPasswordComplexity, InvalidOperation


class UserController():
    """
    UserController

    This class represents the Presentation Layer for the User command.
    """
    password_complexity_constraints = "The password must contain at least 12 characters: " \
                                      "2 uppercase, 2 lowercase, 1 digit, 1 special character"

    def __init__(self, user_logic, user_resource_data):
        self.user_logic=user_logic
        self.user_resource_data=user_resource_data

    def rotate_api_key(self):
        """
        Method that calls to rotate api key logic to perform the rotation
        """
        try:
            # pylint: disable=line-too-long
            resource_to_update, new_api_key = self.user_logic.rotate_api_key(self.user_resource_data.user_id)
            sys.stdout.write(f"Successfully rotated API key for '{resource_to_update}'. " \
                             f"New API key is: {new_api_key}\n")
        except InvalidOperation as invalid_operation:
            raise InvalidOperation("Error: To rotate the API key of the currently logged-in user "\
                                   "use this command without any flags or options") from invalid_operation
        except Exception as general_exception:
            raise general_exception

    # pylint: disable=logging-fstring-interpolation,line-too-long
    def change_personal_password(self):
        """
        Method that calls to change password to perform the change
        """
        self.prompt_for_password()
        try:
            self.user_resource_data.user_id, _ = self.user_logic.change_personal_password(self.user_resource_data.new_password)
        except requests.exceptions.HTTPError as http_error:
            logging.debug(f"Invalid password. {self.password_complexity_constraints}")

            # pylint: disable=line-too-long
            raise InvalidPasswordComplexity(f"Invalid password. {self.password_complexity_constraints}.") from http_error
        logging.debug(f"Successfully changed password for '{self.user_resource_data.user_id}'.")
        sys.stdout.write(f"Successfully changed password for '{self.user_resource_data.user_id}'.\n")

    def prompt_for_password(self):
        """
        Method to prompt user for the password if they did not provide one
        """
        if self.user_resource_data.new_password is None:
            # pylint: disable=line-too-long
            self.user_resource_data.new_password = getpass.getpass(prompt=f"Enter the new password. {self.password_complexity_constraints}: ")
            self.check_password_validity()

    def check_password_validity(self):
        """
        Method for accessing the validity of each password attempt
        """
        # For the future, we can add client-side validations here
        while self.user_resource_data.new_password == '':
            self.user_resource_data.new_password = getpass.getpass(prompt=f"Invalid format. {self.password_complexity_constraints}: ")
