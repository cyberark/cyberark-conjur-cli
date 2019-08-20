import os
from pathlib import Path, PurePath
import shutil
import tempfile
import unittest
import uuid

from conjur.profile import Profile

from yaml import safe_load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class ProfileTest(unittest.TestCase):
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

    ALL_FIELDS_CONFIG = {
      'account': 'myaccount',
      'appliance_url': 'myurl',
      'login_id': 'myloginid',

      'api_key': 'myapikey',
      'ca_bundle': '/cert/file/location',
      'debug': False,
      'insecure': False,
      'password': 'mypassword',
      "tofu": True,
    }

    def setUp(self):
        self._tempdirs = []

    def tearDown(self):
        for temp_dir in self._tempdirs:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def get_profile_path(self, profile_name):
        return os.path.join(self.CURRENT_DIR, 'test_profile', '{}.yml'.format(profile_name))

    def create_temp_config_dir(self, config_from=None):
        tempdir = tempfile.mkdtemp(prefix="{}_".format(self.__class__.__name__))
        self._tempdirs.append(tempdir)

        if config_from:
            shutil.copy(config_from, tempdir)

        return tempdir

    # exists() test

    def test_profile_exists_returns_false_if_file_cannot_be_found(self):
        self.assertFalse(Profile(self.get_profile_path('404')).exists())

    def test_profile_exists_returns_true_if_file_can_be_found(self):
        self.assertTrue(Profile(self.get_profile_path('all_fields')).exists())

    def test_profile_exist_is_realtime_checked(self):
        profile_dir = self.create_temp_config_dir(self.get_profile_path('bad_yaml'))
        profile_path = os.path.join(profile_dir, 'bad_yaml.yml')
        profile = Profile(profile_path)

        self.assertTrue(profile.exists())
        os.remove(profile_path)
        self.assertFalse(profile.exists())


    # create() test

    def test_profile_can_be_created(self):
        profile_dir = self.create_temp_config_dir()
        new_profile_path = os.path.join(profile_dir, 'new_profile.yml')

        Profile(new_profile_path).create('myprofilename', **self.ALL_FIELDS_CONFIG)

        with open(new_profile_path, 'r') as new_profile_file:
            new_profile_data = safe_load(new_profile_file)

        for key, value in self.ALL_FIELDS_CONFIG.items():
            self.assertEqual(new_profile_data[key], value)

    def test_profile_create_returns_the_created_object(self):
        profile_dir = self.create_temp_config_dir()
        new_profile_path = os.path.join(profile_dir, 'new_profile.yml')

        acutal_profile = Profile(new_profile_path).create('myprofilename', **self.ALL_FIELDS_CONFIG)

        with open(new_profile_path, 'r') as new_profile_file:
            expected_profile = safe_load(new_profile_file)

        self.assertEqual(expected_profile, acutal_profile)

    def test_profile_create_saves_the_profile_name(self):
        profile_dir = self.create_temp_config_dir()
        new_profile_path = os.path.join(profile_dir, 'new_profile.yml')

        Profile(new_profile_path).create('myprofilename', **self.ALL_FIELDS_CONFIG)

        with open(new_profile_path, 'r') as new_profile_file:
            new_profile_data = safe_load(new_profile_file)

        self.assertEqual(new_profile_data['name'], 'myprofilename')


    # read() test

    def test_profile_can_be_read(self):
        profile = Profile(self.get_profile_path('all_fields')).read()

        for config_property, config_value in self.ALL_FIELDS_CONFIG.items():
            self.assertIn(config_property, profile)
            error_message = "Profile attribute '{}' was '{}' instead of '{}'!".format(
                config_property, profile[config_property], config_value)
            self.assertEqual(profile[config_property], config_value, error_message)

    def test_profile_read_throws_error_if_file_cannot_be_found(self):
        with self.assertRaises(FileNotFoundError):
            profile = Profile("/foo").read()

    def test_profile_read_throws_error_if_not_valid_yaml(self):
        with self.assertRaises(RuntimeError):
            profile = Profile(self.get_profile_path('bad_yaml')).read()

    def test_profile_read_throws_error_if_required_fields_missing(self):
        with self.assertRaises(RuntimeError):
            profile = Profile(self.get_profile_path('missing_required_fields')).read()

    def test_profile_read_uses_the_name_from_profile_file(self):
        profile = Profile(self.get_profile_path('all_fields')).read()

        self.assertEqual('test', profile['name'])

    def test_profile_read_uses_the_profile_name_if_no_name_field_in_file(self):
        profile = Profile(self.get_profile_path('no_name_profile')).read()

        self.assertEqual('no_name_profile', profile['name'])


    # delete() test

    def test_profile_deletes_removes_the_profile_file(self):
        profile_dir = self.create_temp_config_dir(self.get_profile_path('bad_yaml'))
        profile_path = os.path.join(profile_dir, 'bad_yaml.yml')
        profile = Profile(profile_path)

        self.assertTrue(os.path.exists(profile_path))
        profile.delete()
        self.assertFalse(os.path.exists(profile_path))


    # print()/_repr_() test

    def test_profile_printed_shows_formatted_fields(self):
        stringified_profile = str(Profile(self.get_profile_path('all_fields')))

        self.assertEqual(stringified_profile,
                         "profile:\n" +
                         "    account: myaccount\n" +
                         "    api_key: myapikey\n" +
                         "    appliance_url: myurl\n" +
                         "    ca_bundle: /cert/file/location\n" +
                         "    debug: false\n" +
                         "    insecure: false\n" +
                         "    login_id: myloginid\n" +
                         "    name: test\n" +
                         "    password: mypassword\n" +
                         "    tofu: true\n")
