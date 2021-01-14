# -*- coding: utf-8 -*-

"""
PolicyController module

This module is the controller that facilitates all list actions
required to successfully execute the POLICY command
"""
import sys


class PolicyController:
    """
    PolicyController

    This class represents the Presentation Layer for the POLICY command
    """
    def __init__(self, ssl_verify, policy_logic, policy_data):
        self.ssl_verify = ssl_verify
        self.policy_logic = policy_logic
        self.policy_data = policy_data

    def load(self):
        result = self.policy_logic.run_action(self.policy_data)
        self.print_json_result(result)

    @classmethod
    def print_json_result(cls, result):
        """
        Method to print the JSON of the returned result
        """
        sys.stdout.write(result+'\n')
