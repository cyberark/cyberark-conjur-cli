# -*- coding: utf-8 -*-

"""
Profile module

This module contains all functionality encompasing all the operations on a specific
profile.
"""


class Profile:
    """
    This class provides a low-level programmatic access to a specific profile
    file.
    """

    def __init__(self, profile_path):
        raise NotImplementedError()

    def exists(self):
        """
        This method checks if the profile currently instantiated is present as
        a file on the filesystem.
        """
        raise NotImplementedError()

    def create(self, *args, **kwargs):
        """
        This method creates a profile physical file with the content based on
        the parameters passed in.
        """
        raise NotImplementedError()

    def read(self):
        """
        This method reads the profile's physical file and returns the values
        retrieved from it.
        """
        raise NotImplementedError()

    def update(self, *args, **kwargs):
        """
        This method updates the physical file representing this profile with
        the new values passed in through the parameters
        """
        raise NotImplementedError()

    def delete(self):
        """
        This method deletes the physical file representing this profile.
        """
        raise NotImplementedError()
