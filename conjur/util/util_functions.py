# -*- coding: utf-8 -*-

"""
Utils module

This module holds the common logic across the codebase
"""
import logging
import os

def get_insecure_warning_in_warning():
    """ Log warning message"""
    logging.warning("You chose to initialize the client in insecure mode. "
                    "If you prefer to communicate with the server securely, "
                    "you must reinitialize the client in secure mode.")

def get_insecure_warning_in_debug():
    """ Log debug message"""
    logging.debug("Warning: Running the command with '--insecure' "
                  "makes your system vulnerable to security attacks")

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
