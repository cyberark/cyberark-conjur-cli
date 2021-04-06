# -*- coding: utf-8 -*-

"""
Utils module

This module holds the common logic across the codebase
"""
import logging
import platform
import os

from conjur.util.os_types import OSTypes
from conjur.constants import KEYRING_TYPE_ENV_VARIABLE_NAME, \
    MAC_OS_KEYRING_NAME, LINUX_KEYRING_NAME, WINDOWS_KEYRING_NAME


def get_insecure_warning():
    """ Log warning message"""
    logging.debug("Warning: Running the command with '--insecure'"
                  " makes your system vulnerable to security attacks")

def determine_status_code_specific_error_messages(server_error):
    """ Method for returning status code-specific error messages """
    if str(server_error.response.status_code) == '401':
        return "Failed to log in to Conjur. Unable to authenticate with Conjur. " \
               f"Reason: {server_error}. Check your credentials and try again.\n"
    return f"Failed to execute command. Reason: {server_error}\n"

def file_is_missing_or_empty(file):
    """
    Returns true if the file corresponding to the file argument
    exists or the file size is zero; false otherwise
    """
    return not os.path.exists(file) or os.path.getsize(file) == 0

def configure_env_var_with_keyring():
    """
    Setup the ENV variable for the desired keyring.
    This is important so we will use the exact keyring backend required
    to successfully use the CLI and so that the Third party library will
    not favor another backend
    """
    current_platform = get_current_os()
    if current_platform == OSTypes.MAC_OS:
        os.environ[KEYRING_TYPE_ENV_VARIABLE_NAME] = MAC_OS_KEYRING_NAME
    elif current_platform == OSTypes.LINUX:
        os.environ[KEYRING_TYPE_ENV_VARIABLE_NAME] = LINUX_KEYRING_NAME
    elif current_platform == OSTypes.WINDOWS:
        os.environ[KEYRING_TYPE_ENV_VARIABLE_NAME] = WINDOWS_KEYRING_NAME
    else:
        logging.debug(f"Platform {platform.system()} not supported")

def get_current_os() -> OSTypes: # pragma: no cover
    """
    Determine which os we currently use
    """
    if platform.system() == "Darwin":
        return OSTypes.MAC_OS
    if platform.system() == "Linux":
        return OSTypes.LINUX
    if platform.system() == "Windows":
        return OSTypes.WINDOWS
    return OSTypes.UNKNOWN
