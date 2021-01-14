# -*- coding: utf-8 -*-

"""
PolicyLogic module

This module is the business logic for executing the POLICY command
"""
import json


class PolicyLogic:
    """
    PolicyLogic

    This class holds the business logic for executing and manipulating
    returned data
    """
    def __init__(self, client):
        self.client = client

    def run_action(self, policy_data):
        """
        Method to determine which subcommand action to run {apply, replace, update}
        """
        if policy_data.action == 'replace':
            resources = self.client.replace_policy_file(policy_data.branch, policy_data.file)
        elif policy_data.action == 'update':
            resources = self.client.update_policy_file(policy_data.branch, policy_data.file)
        else:
            resources = self.client.load_policy_file(policy_data.branch, policy_data.file)

        return json.dumps(resources, indent=4)
