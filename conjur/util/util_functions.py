# -*- coding: utf-8 -*-

"""
Utils module

This module holds the common logic across the codebase
"""
import logging


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
