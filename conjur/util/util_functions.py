# -*- coding: utf-8 -*-

"""
Utils module

This module holds the common logic across the codebase
"""

# Builtins
import http
import json
import logging
import platform
import os
import sys

# SDK
from conjur_api.errors.errors import HttpError
from conjur_api.models import SslVerificationMetadata, SslVerificationMode

# Internals
from conjur.errors import MissingRequiredParameterException, InvalidConfigurationException
from conjur.util.os_types import OSTypes
from conjur.data_object.conjurrc_data import ConjurrcData
from conjur.constants import KEYRING_TYPE_ENV_VARIABLE_NAME,MAC_OS_KEYRING_NAME, LINUX_KEYRING_NAME, \
    WINDOWS_KEYRING_NAME, DEFAULT_CERTIFICATE_FILE, DEFAULT_CONFIG_FILE


def list_dictify(obj):
    """
    Function for building a dictionary from all attributes that have values
    """
    list_dict = {}
    for attr, value in obj.__dict__.items():
        if value:
            list_dict[str(attr)] = value

    return list_dict


def get_param(name: str, **kwargs):
    """
    Return value of name if name in kwargs; None otherwise.
    Throws MissingRequiredParameterException in case kwargs is empty or not
    provided
    """
    if len(kwargs) == 0:
        raise MissingRequiredParameterException('arg_params is empty')
    return kwargs[name] if name in kwargs else None


def get_insecure_warning_in_warning():
    """ Log warning message"""
    logging.warning("You chose to initialize the client in insecure mode. "
                    "If you prefer to communicate with the server securely, "
                    "you must reinitialize the client in secure mode.")


def get_insecure_warning_in_debug():
    """ Log debug message"""
    logging.debug("Warning: Running the command with '--insecure' "
                  "makes your system vulnerable to security attacks")


def determine_status_code_specific_error_messages(server_error: HttpError) -> str:
    """ Method for returning status code-specific error messages """
    if server_error.status == http.HTTPStatus.UNAUTHORIZED:
        return "Failed to log in to Conjur. Unable to authenticate with Conjur. " \
               f"Reason: {server_error}. Check your credentials and try again.\n"
    return f"Failed to execute command. Reason: {server_error}\n"


def file_is_missing_or_empty(file_path: str):
    """
    Returns true if the file corresponding to the file argument
    exists or the file size is zero; false otherwise
    """
    return not os.path.exists(file_path) or os.path.getsize(file_path) == 0


# pylint: disable=logging-fstring-interpolation
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


def get_current_os() -> OSTypes:  # pragma: no cover
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


def get_ssl_verification_meta_data_from_conjurrc(ssl_verify: bool,
                                                 conjur_data: ConjurrcData = None) -> SslVerificationMetadata:
    """
    Determine SslVerificationMetaData from conjurrc file
    """
    if not conjur_data:
        conjur_data = ConjurrcData.load_from_file()
    cert_path = conjur_data.cert_file
    if not ssl_verify:
        return SslVerificationMetadata(SslVerificationMode.INSECURE)
    if not cert_path:
        return SslVerificationMetadata(SslVerificationMode.TRUST_STORE)
    if cert_path and cert_path != DEFAULT_CERTIFICATE_FILE:
        return SslVerificationMetadata(SslVerificationMode.CA_BUNDLE, cert_path)
    return SslVerificationMetadata(SslVerificationMode.SELF_SIGN, cert_path)

def get_netrc_path_from_conjurrc(conjur_data: ConjurrcData = None) -> str:
    """
    Determine netrc_path from conjurrc file (if it exists)
    Ignore any conjurrc errors here since this gets called
    before the CLI's main exception handling block
    """
    if conjur_data is None and os.path.exists(DEFAULT_CONFIG_FILE):
        try:
            conjur_data = ConjurrcData.load_from_file()
        except InvalidConfigurationException:
            pass

    if hasattr(conjur_data, "netrc_path") and conjur_data.netrc_path is not None:
        return conjur_data.netrc_path
    return None

def print_json_result(result):
    """
    Method to print the JSON of the returned result
    """
    sys.stdout.write(f"{json.dumps(result, indent=4)}\n")
