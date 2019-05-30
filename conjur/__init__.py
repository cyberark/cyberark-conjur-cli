"""
Main module

This metafile includes all the functionality that will be exposed
when you install this module
"""

import sys

if sys.version_info < (3,):
    raise ImportError("""You are running Conjur Python3 APIs on Python 2

This package is not compatible with Python 2, and you still ended up
with this version installed which should not have happened. Make sure you
have pip >= 9.0 to avoid this kind of issue, as well as setuptools >= 24.2:

 $ pip install pip setuptools --upgrade

Your choices:

- Upgrade to Python 3.

- Install an older version of Conjur APIs:

 $ pip install Conjur
""")

#pylint: disable=wrong-import-position
from .client import Client
#pylint: disable=wrong-import-position
from .cli import Cli
