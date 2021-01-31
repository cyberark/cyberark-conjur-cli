# -*- coding: utf-8 -*-

"""
HostController module

This module is the controller that facilitates all host actions
"""

# Builtins
import sys
# Allows users to move left and right when inputting input instead of printing escape characters
# https://stackoverflow.com/questions/58591423/python-prints-escape-keys-while-entering-input-when-pressing-the-arrow-keys-on-t
# pylint: disable=unused-import
import readline

# Internals
from conjur.errors import MissingRequiredParameterException
from conjur.resource import Resource


class HostController():
    """
    HostController

    This class represents the Presentation Layer for the User command.
    """
    def __init__(self, client, host_resource_data):
        self.client=client
        self.host_resource_data=host_resource_data

    def rotate_api_key(self):
        """
        Method that distinguishes between the type of actions
        and facilitates the calls accordingly
        """
        self.prompt_for_host_id_if_needed()

        resource = Resource(type_='host',
                            name=self.host_resource_data.host_to_update)
        new_api_key = self.client.rotate_other_api_key(resource)
        # pylint: disable=line-too-long
        sys.stdout.write(f"Successfully rotated API key for '{self.host_resource_data.host_to_update}' "
                         f"New API key is: {new_api_key}\n")

    def prompt_for_host_id_if_needed(self):
        """
        Method to prompt the user to enter the host id of the
        host whose API key they want to rotate
        """
        if self.host_resource_data.host_to_update is None:
            # pylint: disable=line-too-long
            self.host_resource_data.host_to_update = input("Enter the host id to rotate its API key: ").strip()
            if self.host_resource_data.host_to_update  == '':
                # pylint: disable=raise-missing-from
                raise MissingRequiredParameterException("Error: Host id is required")
