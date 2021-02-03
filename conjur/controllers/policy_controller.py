# -*- coding: utf-8 -*-

"""
PolicyController module

This module is the controller that facilitates all list actions
required to successfully execute the POLICY command
"""
import sys

# pylint: disable=too-few-public-methods
import requests

from conjur.errors import InvalidFormatException


class PolicyController:
    """
    PolicyController

    This class represents the Presentation Layer for the POLICY command
    """
    def __init__(self, policy_logic, policy_data):
        self.policy_logic = policy_logic
        self.policy_data = policy_data

    def load(self):
        """
        Method that facilitates all method calls in this class
        """
        try:
            result = self.policy_logic.run_action(self.policy_data)
            sys.stdout.write(result+'\n')
        except requests.exceptions.HTTPError as http_error:
            if http_error.response.status_code == 422:
                raise InvalidFormatException(f"{http_error}. The policy was empty or its contents "
                                             "were not in valid YAML.") from http_error
            raise
