import os
import unittest

from conjur.config import Config

class ConfigTest(unittest.TestCase):
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

    GOOD_CONJURRC = os.path.join(CURRENT_DIR, 'test_config', 'good_conjurrc')
    GOOD_NETRC = os.path.join(CURRENT_DIR, 'test_config', 'good_netrc')

    MISSING_ACCOUNT_CONJURRC = os.path.join(CURRENT_DIR, 'test_config', 'missing_account_conjurrc')
    MISSING_URL_CONJURRC = os.path.join(CURRENT_DIR, 'test_config', 'missing_url_conjurrc')
    MISSING_MACHINE_NETRC = os.path.join(CURRENT_DIR, 'test_config', 'missing_machine_netrc')

    EXPECTED_CONFIG = {
      'account': 'accountname',
      'api_key': 'conjurapikey',
      'ca_bundle': '/cert/file/location',
      'login_id': 'someadmin',
      'plugins': ['foo', 'bar'],
      'url': 'https://someurl/somepath',
    }

    def test_config_loading_works(self):
        Config(config_file=self.GOOD_CONJURRC, netrc_file=self.GOOD_NETRC)

    def test_config_has_appropriate_attributes(self):
        test_data = Config(config_file=self.GOOD_CONJURRC, netrc_file=self.GOOD_NETRC)

        for config_property, config_value in self.EXPECTED_CONFIG.items():
            error_message = "Config attribute '{}' was '{}' instead of '{}'!".format(
                config_property, getattr(test_data,config_property), config_value)
            self.assertEqual(getattr(test_data,config_property), config_value, error_message)

    def test_config_dictionary_has_appropriate_map(self):
        test_data = dict(Config(config_file=self.GOOD_CONJURRC, netrc_file=self.GOOD_NETRC))

        for config_property, config_value in self.EXPECTED_CONFIG.items():
            error_message = "Config field '{}' was '{}' instead of '{}'!".format(
                config_property, test_data[config_property], config_value)
            self.assertEqual(test_data[config_property], config_value, error_message)

    def test_config_printed_shows_formatted_fields(self):
        test_data = str(Config(config_file=self.GOOD_CONJURRC, netrc_file=self.GOOD_NETRC))

        self.assertEquals(test_data,
            "config:\n" +
            "    account: accountname\n" +
            "    api_key: conjurapikey\n" +
            "    ca_bundle: /cert/file/location\n" +
            "    login_id: someadmin\n" +
            "    plugins:\n" +
            "    - foo\n" +
            "    - bar\n" +
            "    url: https://someurl/somepath\n")

    def test_config_with_no_conjurrc_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            Config(config_file='/tmp/foo', netrc_file=self.GOOD_NETRC)

    def test_config_with_no_netrc_raises_error(self):
        with self.assertRaises(FileNotFoundError):
            Config(config_file=self.GOOD_CONJURRC, netrc_file='/tmp/bar')

    def test_config_with_no_netrc_entry_raises_error(self):
        with self.assertRaises(RuntimeError):
            Config(config_file=self.GOOD_CONJURRC, netrc_file=self.MISSING_MACHINE_NETRC)

    def test_config_with_no_conjurrc_account_raises_error(self):
        with self.assertRaises(AssertionError):
            Config(config_file=self.MISSING_ACCOUNT_CONJURRC, netrc_file=self.GOOD_NETRC)

    def test_config_with_no_conjurrc_url_raises_error(self):
        with self.assertRaises(AssertionError):
            Config(config_file=self.MISSING_URL_CONJURRC, netrc_file=self.GOOD_NETRC)
