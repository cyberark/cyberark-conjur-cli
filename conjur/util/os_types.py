"""
OSTypes module
This module is used to represent different os platforms.
"""

from enum import Enum


class OSTypes(Enum):   # pragma: no cover
    """
    Represent possible platforms that the cli might be running on
    """
    UNKNOWN = 0
    WINDOWS = 1
    MAC_OS = 2
    LINUX = 3
