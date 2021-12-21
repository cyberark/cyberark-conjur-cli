"""
SslVerificationMode module
This module is used to represent different types of SSL verification options
"""
from enum import Enum


class SslVerificationMode(Enum):
    """
    Enumeration of all possible certificate methods that we may use against
    """
    TRUST_STORE = 0
    CA_BUNDLE = 1
    SELF_SIGN = 2
    INSECURE = 3  # Skip cert validation
