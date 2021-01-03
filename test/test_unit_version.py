import unittest

from conjur.version import __version__

class VersionTest(unittest.TestCase):
    def test_version_is_set(self):
        self.assertIsNotNone(__version__)

