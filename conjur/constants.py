# -*- coding: utf-8 -*-

"""
Constants module

This module holds all constants used across the codebase
"""

# Builtins
import os
import platform

# The OS the CLI is run on is determined by the following:
# See https://stackoverflow.com/questions/1854/python-what-os-am-i-running-on
# pylint: disable=no-member
if os.name != "posix" and platform.system() == "Windows":
    INTERNAL_FILE_PREFIX="_"

else:
    INTERNAL_FILE_PREFIX="."

DEFAULT_NETRC_FILE_NAME = INTERNAL_FILE_PREFIX + "netrc"

DEFAULT_CONFIG_FILE = os.path.expanduser(os.path.join('~', '.conjurrc'))
DEFAULT_NETRC_FILE = os.path.expanduser(os.path.join('~', DEFAULT_NETRC_FILE_NAME))
DEFAULT_CERTIFICATE_FILE = os.path.expanduser(os.path.join('~', "conjur-server.pem"))

VALID_CONFIRMATIONS = ["yes", "y"]

SUPPORTED_BACKENDS = ["macOS Keyring", "Windows WinVaultKeyring", "SecretService Keyring"]

MACHINE = "machine"
LOGIN = "login"
PASSWORD = "password"
KEYSTORE_ATTRIBUTES = [MACHINE, LOGIN, PASSWORD]

# For testing purposes
TEST_HOSTNAME = "https://conjur-https"
TEST_KEYRING = "SecretService Keyring"

# For user interaction
LOGIN_IS_REQUIRED = "To start using the CLI, log in to Conjur"

# For keyring environment configuration
KEYRING_TYPE_ENV_VARIABLE_NAME = "PYTHON_KEYRING_BACKEND"
MAC_OS_KEYRING_NAME = "keyring.backends.macOS.Keyring"
LINUX_KEYRING_NAME = "keyring.backends.SecretService.Keyring"
WINDOWS_KEYRING_NAME = "keyring.backends.Windows.WinVaultKeyring"
