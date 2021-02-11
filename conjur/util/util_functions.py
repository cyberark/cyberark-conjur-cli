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
