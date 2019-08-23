# -*- coding: utf-8 -*-

"""
ProfileManager module

This module contains all functionality needed to interact with
profile management on the user's system
"""

import os
from pathlib import Path, PurePath

from .profile import Profile


class ProfileManager:
    """
    This class provides a high-level management and use capabilities to a
    group of co-located profiles on the system.
    """

    CONFIG_DIR_NAME = '.conjur'
    DEFAULT_PROFILE_CONFIG_FILE = 'default_profile'

    PROFILE_NOT_FOUND_ERROR = "ERROR: Profile file '{}.yml' not found!"

    def __init__(self, base_dir=None):
        if not base_dir:
            base_dir = Path.home()

        self._config_dir = PurePath.joinpath(Path(os.path.expanduser(base_dir)),
                                             ProfileManager.CONFIG_DIR_NAME)

        self._default_profile_config_file = \
                PurePath.joinpath(self._config_dir,
                                  ProfileManager.DEFAULT_PROFILE_CONFIG_FILE)

    def _profile_file(self, profile_name):
        return PurePath.joinpath(Path(self.config_dir),
                                 '{}.yml'.format(profile_name))

    @property
    def config_dir(self):
        """
        This property returns the directory that the class is using to base its
        operations on.
        """
        return self._config_dir.as_posix()

    @property
    def default_profile_config_file(self):
        """
        This property returns the physicla file path that points to the profile
        that is determined to be the default one in the `config_dir`.
        """
        return self._default_profile_config_file.as_posix()

    def list(self):
        """
        This method returns a list of profiles available in the directory
        that the manager was initialized with.
        """

        # If directory doesn't exist, just return nothing
        if not Path(self.config_dir).is_dir():
            return []

        # Get all items in that directory
        fs_items = sorted(Path(self.config_dir).iterdir())

        # Filter out non-yaml files
        filtered_fs_items = filter(lambda fs_item: fs_item.suffixes == ['.yml'], fs_items)

        # Trim out the extensions
        basenames = map(lambda fs_item: fs_item.stem, filtered_fs_items)

        # Filter out 'default' profile
        profiles = filter(lambda basename: basename != 'default', basenames)

        return list(profiles)

    @property
    def current(self):
        """
        This method retrieves the default profile names based on the continent
        of the directory with which the manager was initialized.
        """

        default_profile_config_file = Path(self.default_profile_config_file)

        # Fallback. Check if there's only one profile and if that's the case, use that
        # but if the default is not defined and we have multiple profiles, bail with
        # an error.
        if not default_profile_config_file.is_file():
            profiles = self.list()

            if len(profiles) == 1:
                return profiles[0]

            return None

        profile_name = Path(default_profile_config_file).read_text()
        profile_name = profile_name.strip()

        if not profile_name:
            return None

        default_profile_file = self._profile_file(profile_name)

        # PyLint doesn't have up-to-date member listing of pathlib methods
        #pylint: disable=no-member
        resolved_profile_file = default_profile_file.resolve()
        if not resolved_profile_file.is_file():
            raise RuntimeError(self.PROFILE_NOT_FOUND_ERROR.format(resolved_profile_file))

        return profile_name

    def set_default(self, profile_name):
        """
        This method sets the default profile name persistently.
        """

        target_profile_file = self._profile_file(profile_name)

        # PyLint doesn't have up-to-date member listing of pathlib methods
        #pylint: disable=no-member
        if not target_profile_file.is_file():
            raise OSError(self.PROFILE_NOT_FOUND_ERROR.format(target_profile_file))

        # TODO: This isn't thread-safe so eventually
        #       we should make it so
        with open(self.default_profile_config_file, 'w') as config_file:
            config_file.write(profile_name)

    def create(self, profile_name, **kwargs):
        """
        This method creates a profile in the config_dir with the specified name
        and specified arguments. The method returns the profile object created.
        """
        return Profile(self._profile_file(profile_name)).create(**kwargs)

    def read(self, profile_name):
        """
        This method reads the profile in the config_dir with the specified name
        and returns the profile object.
        """
        return Profile(self._profile_file(profile_name))

    def delete(self, profile_name):
        """
        This method deletes a profile in the config_dir with the specified name.
        """
        return Profile(self._profile_file(profile_name)).delete()
