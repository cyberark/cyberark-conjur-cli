# -*- coding: utf-8 -*-
"""
Error module

This module holds SSL wrapper specific errors for this project
"""
# Builtin
from socket import gaierror


class TLSSocketConnectionException(Exception):
    """ Thrown to indicate TLS Socket exception. """

    def __init__(self, err: gaierror):
        super().__init__(str(err))


class TLSGeneralException(Exception):
    """ Thrown to indicate TLS General exception. """
