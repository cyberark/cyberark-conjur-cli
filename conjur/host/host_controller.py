# -*- coding: utf-8 -*-

"""
HostController module

This module is the controller that facilitates all host actions
"""

# Builtins
import sys

class HostController():
    """
    HostController

    This class represents the Presentation Layer for the User command.
    """
    def __init__(self, client, host_resource_data):
        self.client=client
        self.host_resource_data=host_resource_data

    def rotate_api_key(self, resource):
        """
        Method that distinguishes between the type of actions
        and facilitates the calls accordingly
        """
        self.prompt_for_host_id()
        new_api_key = self.client.rotate_anothers_api_key(resource,
                                                          self.host_resource_data.host_to_update)
        sys.stdout.write(f"API key for '{self.host_resource_data.host_to_update}' " \
                        f"was successfully rotated. New API key is: {new_api_key}\n")

    def prompt_for_host_id(self):
        """
        Method to prompt the user to enter the host id of the
        host whose API key they want to rotate
        """
        if self.host_resource_data.host_to_update is None:
            # pylint: disable=line-too-long
            self.host_resource_data.host_to_update = input("Enter the host id whose API key to rotate: ").strip()
            if self.host_resource_data.host_to_update  == '':
                # pylint: disable=raise-missing-from
                raise RuntimeError("Error: Host id is required")
