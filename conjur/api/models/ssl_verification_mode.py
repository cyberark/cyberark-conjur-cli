"""
SslVerificationMode module
This module is used to represent different types of SSL verification options
"""
from enum import Enum


class SslVerificationMode(Enum):
    """
    Enumeration of all possible certificate methods that we may use against
    """
    WITH_TRUST_STORE = 0
    WITH_CA_BUNDLE = 1
    SELF_SIGN = 2
    NO_SSL = 3 # TODO rename to no_cert_validation
