# -*- coding: utf-8 -*-

"""
UserController module

This module is the controller that facilitates all user actions
"""

# Builtins
import getpass
import http
import logging
import sys

# Internals
from conjur.errors import InvalidPasswordComplexityException, \
    OperationNotCompletedException
from conjur_api.errors.errors import HttpError, HttpStatusError
from conjur.errors_messages import PASSWORD_COMPLEXITY_CONSTRAINTS_MESSAGE
from conjur.logic.user_logic import UserLogic
from conjur.data_object.user_input_data import UserInputData


class UserController:
    """
    UserController

    This class represents the Presentation Layer for the User command.
    """

    def __init__(self, user_logic: UserLogic, user_input_data: UserInputData):
        self.user_logic = user_logic
        self.user_input_data = user_input_data

    def rotate_api_key(self):
        """
        Method that calls to rotate api key logic to perform the rotation
        """
        try:
            # pylint: disable=line-too-long
            resource_to_update, new_api_key = self.user_logic.rotate_api_key(self.user_input_data.user_id)
            sys.stdout.write(f"Successfully rotated API key for '{resource_to_update}'."'\n'
                             f"New API key is: {new_api_key}\n")
        except OperationNotCompletedException:
            sys.stdout.write("An error occurred. Log in again or try again in debug mode.\n")
            raise

    # pylint: disable=logging-fstring-interpolation,line-too-long
    def change_personal_password(self):
        """
        Method that calls to change password to perform the change
        """
        self.prompt_for_password()
        try:
            self.user_input_data.user_id = self.user_logic.change_personal_password(self.user_input_data.new_password)
        except HttpError as http_error:
            # pylint: disable=no-member
            if isinstance(http_error, HttpStatusError) and http_error.status == http.HTTPStatus.UNAUTHORIZED:
                raise

            logging.debug(f"Invalid password {PASSWORD_COMPLEXITY_CONSTRAINTS_MESSAGE}")
            # pylint: disable=line-too-long
            raise InvalidPasswordComplexityException("Error: Invalid password "
                                                     f"{PASSWORD_COMPLEXITY_CONSTRAINTS_MESSAGE}.") from http_error
        logging.debug(f"Successfully changed password for '{self.user_input_data.user_id}'.")
        sys.stdout.write(f"Successfully changed password for '{self.user_input_data.user_id}'.\n")

    def prompt_for_password(self):
        """
        Method to prompt user for the password if they did not provide one
        """
        if self.user_input_data.new_password is None:
            # pylint: disable=line-too-long
            self.user_input_data.new_password = getpass.getpass(
                prompt=f"Enter the new password {PASSWORD_COMPLEXITY_CONSTRAINTS_MESSAGE}: ")
            self.check_password_validity()

    def check_password_validity(self):
        """
        Method for accessing the validity of each password attempt
        """
        # For the future, we can add client-side validations here
        while self.user_input_data.new_password == '':
            self.user_input_data.new_password = getpass.getpass(
                prompt=f"Invalid format {PASSWORD_COMPLEXITY_CONSTRAINTS_MESSAGE}: ")
