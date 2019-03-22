import unittest

from conjur_api_python3.http import HttpVerb

class HttpVerbTest(unittest.TestCase):
    def test_http_verb_has_all_the_verbs_expected(self):
        self.assertTrue(HttpVerb.GET)
        self.assertTrue(HttpVerb.PUT)
        self.assertTrue(HttpVerb.POST)
        self.assertTrue(HttpVerb.DELETE)
