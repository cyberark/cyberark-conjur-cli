# -*- coding: utf-8 -*-

"""
Error module

This module holds Conjur CLI/SDK-specific error messages for this project
"""

# pylint: disable=line-too-long
INCONSISTENT_VERIFY_MODE_MESSAGE = "The client was initialized without certificate verification, even though the " \
                                  "command was ran with certificate verification enabled. To continue communicating " \
                                  "with the server insecurely, run the command again with --insecure flag. " \
                                  "Otherwise, reinitialize the client."

PASSWORD_COMPLEXITY_CONSTRAINTS_MESSAGE = "(it must contain at least 12 characters: " \
                                          "2 uppercase, 2 lowercase, 1 digit, 1 special character)"

# pylint: disable=line-too-long
MISMATCH_HOSTNAME_MESSAGE = "The machine's hostname did not match any names on the certificate. " \
                            "Make sure the names on the certificate (common name or SANs) match the machine's hostname."

FETCH_CREDENTIALS_FAILURE_MESSAGE = "Failed to fetch credentials. Log in again and try again."
