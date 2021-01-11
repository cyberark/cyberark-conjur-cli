# -*- coding: utf-8 -*-

"""
Utils module

This module holds the common logic across the codebase
"""
import logging


class Utils:
    @classmethod
    def get_insecure_warning(cls):
        logging.debug("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks")
