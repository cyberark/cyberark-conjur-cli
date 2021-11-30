# -*- coding: utf-8 -*-

"""
SSLClient module

This module holds all of ssl_utils consts
"""

from OpenSSL import SSL
CONJUR_TLS_METHODS = {
    "1.0": SSL.TLSv1_METHOD,
    "1.1": SSL.TLSv1_1_METHOD,
    "1.2": SSL.TLSv1_2_METHOD,
    "1.3": SSL.SSLv23_METHOD
}
