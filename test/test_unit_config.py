import os
import re
import unittest

from conjur.config import Config

class ConfigTest(unittest.TestCase):
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

    GOOD_CONJURRC = os.path.join(CURRENT_DIR, 'test_config', 'good_conjurrc')

    MISSING_ACCOUNT_CONJURRC = os.path.join(CURRENT_DIR, 'test_config', 'missing_account_conjurrc')
    MISSING_URL_CONJURRC = os.path.join(CURRENT_DIR, 'test_config', 'missing_url_conjurrc')

    EXPECTED_CONFIG = {
      'account': 'accountname',
      'ca_bundle': '/cert/file/location',
      'plugins': ['foo', 'bar'],
      'url': 'https://someurl/somepath',
    }

    def test_config_loading_works(self):
        Config(config_file=self.GOOD_CONJURRC)

    def test_config_has_appropriate_attributes(self):
        test_data = Config(config_file=self.GOOD_CONJURRC)

        for config_property, config_value in self.EXPECTED_CONFIG.items():
            error_message = "Config attribute '{}' was '{}' instead of '{}'!".format(
                config_property, getattr(test_data,config_property), config_value)
            self.assertEqual(getattr(test_data,config_property), config_value, error_message)

    def test_config_dictionary_has_appropriate_map(self):
        test_data = dict(Config(config_file=self.GOOD_CONJURRC))

        for config_property, config_value in self.EXPECTED_CONFIG.items():
            error_message = "Config field '{}' was '{}' instead of '{}'!".format(
                config_property, test_data[config_property], config_value)
            self.assertEqual(test_data[config_property], config_value, error_message)


    def test_config_printed_shows_formatted_fields(self):
        test_data = str(Config(config_file=self.GOOD_CONJURRC))

        self.assertRegex(test_data,
            re.compile(
                "^config:\n" +
                "\s+account: accountname\n" +
                "\s+ca_bundle: /cert/file/location\n" +
                "\s+plugins:.*foo.*bar.*\n" +
                "\s+url: https://someurl/somepath\n",
                re.MULTILINE | re.DOTALL,
            ))

    def test_config_with_no_conjurrc_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            Config(config_file='/tmp/foo')

    def test_config_with_no_conjurrc_account_raises_error(self):
        with self.assertRaises(AssertionError):
            Config(config_file=self.MISSING_ACCOUNT_CONJURRC)

    def test_config_with_no_conjurrc_url_raises_error(self):
        with self.assertRaises(AssertionError):
            Config(config_file=self.MISSING_URL_CONJURRC)
