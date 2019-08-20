# -*- coding: utf-8 -*-

"""
Profile module

This module contains all functionality encompasing all the operations on a specific
profile.
"""

import os
from pathlib import Path, PurePath

from yaml import load, dump
try:
    from yaml import CSafeLoader as SafeLoader, CDumper as Dumper
except ImportError:
    from yaml import SafeLoader, Dumper


class Profile:
    """
    This class provides a low-level programmatic access to a specific profile
    file.
    """

    REQUIRED_FIELDS = [
        "account",
        "appliance_url",
        "login_id",
    ]

    def __init__(self, profile_path):
        self._profile_path = Path(profile_path).resolve()

    def __repr__(self):
        return dump({'profile': self.read()}, default_flow_style=False, Dumper=Dumper, indent=4)

    def exists(self):
        """
        This method checks if the profile currently instantiated is present as
        a file on the filesystem.
        """
        return self._profile_path.exists()

    def create(self, profile_name, **kwargs):
        """
        This method creates a profile physical file with the content based on
        the parameters passed in.
        """
        kwargs['name'] = profile_name

        with open(self._profile_path, 'w') as output_file:
            dump(kwargs, output_file, default_flow_style=False, indent=4)

        return self.read()

    def read(self):
        """
        This method reads the profile's physical file and returns the values
        retrieved from it.
        """

        profile = None
        with open(self._profile_path, 'r') as stream:
            profile = load(stream, Loader=SafeLoader)

        errors = []
        for field in self.REQUIRED_FIELDS:
            if field not in profile:
                errors.append("Missing '{}' field".format(field))

        if errors:
            raise RuntimeError("Error reading profile: {}".format(errors))

        if not 'name' in profile:
            profile['name'] = PurePath(self._profile_path).stem

        return profile

    def delete(self):
        """
        This method deletes the physical file representing this profile.
        """
        os.remove(self._profile_path)
