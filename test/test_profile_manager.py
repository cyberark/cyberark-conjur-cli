import os
from pathlib import Path, PurePath
import shutil
import tempfile
import unittest
import uuid

from unittest.mock import patch

from conjur.profile_manager import ProfileManager

class ProfileManagerTest(unittest.TestCase):
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

    SINGLE_PROFILE_NO_CONFIG_DIR = os.path.join(CURRENT_DIR, 'test_profile_manager', 'single_profile')
    BASIC_PROFILE_DIR = os.path.join(CURRENT_DIR, 'test_profile_manager', 'basic_profile')
    MULTI_PROFILE_DIR = os.path.join(CURRENT_DIR, 'test_profile_manager', 'multiple_profiles')

    EXPECTED_MULTI_PROFILES = [
        '12345',
        'profile1',
        'profile2',
        'profile3',
        'profile4',
        'profile5',
    ]

    def setUp(self):
        self._tempdirs = []

    def tearDown(self):
        for temp_dir in self._tempdirs:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def generate_random_string(self):
        return uuid.uuid4().hex

    def create_temp_config_dir(self, config_from=None):
        tempdir = tempfile.mkdtemp(prefix="{}_".format(self.__class__.__name__))
        self._tempdirs.append(tempdir)

        conjur_dir = os.path.join(tempdir, ProfileManager.CONFIG_DIR_NAME)

        if not config_from:
            Path(conjur_dir).mkdir(parents=False, exist_ok=True)
        else:
            shutil.copytree(config_from, conjur_dir, symlinks=True,
                            ignore_dangling_symlinks=True)

        return tempdir


    # config_dir() tests

    def test_config_dir_is_based_on_expected_suffix(self):
        self.assertEqual(ProfileManager(base_dir='/foo/bar').config_dir,
                         '/foo/bar/.conjur')

    def test_config_dir_expands_tilde(self):
        self.assertEqual(ProfileManager(base_dir='~/foo/bar').config_dir,
                         os.path.join(os.environ.get('HOME'), 'foo/bar/.conjur'))

    def test_config_dir_is_rooted_in_homedir_when_basedir_not_defined(self):
        self.assertEqual(ProfileManager().config_dir,
                         os.path.join(os.environ.get('HOME'), '.conjur'))


    # default_profile_config_file() tests

    def test_default_profile_config_file_is_based_on_expected_suffix(self):
        self.assertEqual(ProfileManager(base_dir='/foo/bar').default_profile_config_file,
                         os.path.join('/foo/bar', '.conjur', 'default_profile'))

    def test_default_profile_config_file_is_rooted_in_homedir_when_basedir_not_defined(self):
        self.assertEqual(ProfileManager().default_profile_config_file,
                         os.path.join(os.environ.get('HOME'), '.conjur', 'default_profile'))


    # current() tests

    def test_current_profile_is_none_if_default_profile_missing_and_no_profiles(self):
        base_dir = self.create_temp_config_dir()
        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, None)

    def test_current_profile_is_none_if_default_profile_file_missing_and_no_yml_files(self):
        base_dir = self.create_temp_config_dir()

        for test_ext in ["txt", "json", "foo", "yolo"]:
            config = os.path.join(base_dir,
                                  ProfileManager.CONFIG_DIR_NAME,
                                  "{}.{}".format(self.generate_random_string(), test_ext))
            open(config, 'a').close()

        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, None)

    def test_current_profile_is_set_correctly_if_no_default_profile_file_and_single_yml_file(self):
        base_dir = self.create_temp_config_dir()

        for test_ext in ["txt", "json", "foo", "yaml"]:
            config = os.path.join(base_dir,
                                  ProfileManager.CONFIG_DIR_NAME,
                                  "{}.{}".format(self.generate_random_string(), test_ext))
            open(config, 'a').close()

        profile_name = self.generate_random_string()
        profile_yml = os.path.join(base_dir,
                                   ProfileManager.CONFIG_DIR_NAME,
                                   "{}.{}".format(profile_name, "yml"))
        open(profile_yml, 'a').close()

        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, profile_name)

    def test_current_profile_is_none_if_no_default_profile_file_and_multiple_yml_file(self):
        base_dir = self.create_temp_config_dir()

        for _ in range(0, 10):
            config = os.path.join(base_dir,
                                  ProfileManager.CONFIG_DIR_NAME,
                                  "{}.{}".format(self.generate_random_string(), "yml"))
            open(config, 'a').close()

        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, None)

    def test_current_profile_is_none_if_default_is_not_a_real_file(self):
        base_dir = self.create_temp_config_dir()
        config_file = os.path.join(base_dir,
                                   ProfileManager.CONFIG_DIR_NAME,
                                   ProfileManager.DEFAULT_PROFILE_CONFIG_FILE)
        os.makedirs(config_file)

        self.assertEqual(ProfileManager(base_dir=base_dir).current, None)

    def test_current_profile_with_single_profile_uses_name_from_linked_default_profile_file(self):
        base_dir = self.create_temp_config_dir(self.BASIC_PROFILE_DIR)
        self.assertEqual(ProfileManager(base_dir=base_dir).current, 'profile1')

    def test_current_profile_with_multiple_profiles_uses_name_from_default_profile_file(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)
        self.assertEqual(ProfileManager(base_dir=base_dir).current, 'profile3')

    def test_current_profile_updates_based_on_underlying_fs_state(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)

        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, 'profile3')

        default_profile_config_file = os.path.join(base_dir,
                                                   ProfileManager.CONFIG_DIR_NAME,
                                                   ProfileManager.DEFAULT_PROFILE_CONFIG_FILE)

        with open(default_profile_config_file, 'w') as config_file:
            config_file.write("profile2")

        self.assertTrue(Path(default_profile_config_file).exists())
        self.assertEqual(profile_manager.current, 'profile2')

    def test_current_profile_returns_none_if_profile_in_default_profile_is_empty(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)

        default_profile_config_file = os.path.join(base_dir,
                                                   ProfileManager.CONFIG_DIR_NAME,
                                                   ProfileManager.DEFAULT_PROFILE_CONFIG_FILE)

        with open(default_profile_config_file, 'w') as config_file:
            config_file.write("")

        self.assertTrue(Path(default_profile_config_file).exists())

        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, None)

    def test_current_profile_returns_correct_profile_if_linefeeds_are_present(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)

        default_profile_config_file = os.path.join(base_dir,
                                                   ProfileManager.CONFIG_DIR_NAME,
                                                   ProfileManager.DEFAULT_PROFILE_CONFIG_FILE)

        with open(default_profile_config_file, 'w') as config_file:
            config_file.write("profile2\r\n")

        self.assertTrue(Path(default_profile_config_file).exists())

        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, "profile2")

    def test_current_profile_returns_none_if_default_profile_doesnt_exist(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)

        default_profile_config_file = os.path.join(base_dir,
                                                   ProfileManager.CONFIG_DIR_NAME,
                                                   ProfileManager.DEFAULT_PROFILE_CONFIG_FILE)

        with open(default_profile_config_file, 'w') as config_file:
            config_file.write("profile123")

        self.assertTrue(Path(default_profile_config_file).exists())

        profile_manager = ProfileManager(base_dir=base_dir)
        with self.assertRaises(RuntimeError):
            profile_manager.current


    # list() test

    def test_listing_returns_no_profiles_if_none_are_defined(self):
        base_dir = self.create_temp_config_dir()
        self.assertEqual(ProfileManager(base_dir=base_dir).list(), [])

    def test_listing_returns_no_profiles_if_profile_dir_is_missing(self):
        base_dir = self.create_temp_config_dir()
        self.assertEqual(ProfileManager(base_dir=os.path.join(base_dir, 'foo')).list(), [])

    def test_listing_returns_all_profiles(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)
        self.assertEqual(ProfileManager(base_dir=base_dir).list(), self.EXPECTED_MULTI_PROFILES)

    def test_listing_returns_only_yml_files(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)
        for filename in ['blah.foo', 'foo', 'stuff.yaml', 'things.yml.foo']:
            config = os.path.join(base_dir, ProfileManager.CONFIG_DIR_NAME,
                                  filename)
            open(config, 'a').close()

        self.assertEqual(ProfileManager(base_dir=base_dir).list(), self.EXPECTED_MULTI_PROFILES)


    # set_default() test

    def test_set_default_profile_changes_instance_current_selection(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)

        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, 'profile3')

        profile_manager.set_default('profile2')
        self.assertEqual(profile_manager.current, 'profile2')

    def test_set_default_profile_doesnt_create_default_config_file_if_only_one_profile_and_selected(self):
        base_dir = self.create_temp_config_dir(self.SINGLE_PROFILE_NO_CONFIG_DIR)

        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, 'single_profile_config')

        profile_manager.set_default('single_profile_config')
        self.assertEqual(profile_manager.current, 'single_profile_config')

        self.assertFalse(PurePath.joinpath(Path(base_dir),
                                           ProfileManager.DEFAULT_PROFILE_CONFIG_FILE).is_file())

    def test_set_default_profile_changes_default_permanently(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)

        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, 'profile3')
        profile_manager.set_default('profile1')

        new_profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(new_profile_manager.current, 'profile1')

    def test_setting_default_profile_fails_when_profile_does_not_exist(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)

        profile_manager = ProfileManager(base_dir=base_dir)
        with self.assertRaises(OSError):
            profile_manager.set_default('doesnotexist')

    def test_setting_default_profile_does_not_change_current_profile_when_setting_fails(self):
        base_dir = self.create_temp_config_dir(self.MULTI_PROFILE_DIR)

        profile_manager = ProfileManager(base_dir=base_dir)
        self.assertEqual(profile_manager.current, 'profile3')

        with self.assertRaises(OSError):
            profile_manager.set_default('doesnotexist')

        self.assertEqual(profile_manager.current, 'profile3')


    # create() test

    @patch('conjur.profile_manager.Profile')
    def test_creating_profile_delegates_to_profile_class(self, profile_instance):
        base_dir = self.create_temp_config_dir(self.SINGLE_PROFILE_NO_CONFIG_DIR)
        profile_manager = ProfileManager(base_dir=base_dir)
        expected_profile_path = PurePath.joinpath(Path(profile_manager.config_dir),
                                                  'test_profile.yml')

        kwargs = {
            "foo": "fooval",
            "bar": "barval",
        }

        profile_manager.create("test_profile", **kwargs)

        profile_instance.assert_called_with(expected_profile_path)
        profile_instance.return_value.create.assert_called_with(**kwargs)

    @patch('conjur.profile_manager.Profile')
    def test_creating_profile_returns_profile_instance(self, profile_instance):
        base_dir = self.create_temp_config_dir(self.SINGLE_PROFILE_NO_CONFIG_DIR)
        profile_manager = ProfileManager(base_dir=base_dir)

        actual_profile = profile_manager.create("profile_name")

        self.assertEqual(profile_instance.return_value.create.return_value, actual_profile)

    # read() test

    @patch('conjur.profile_manager.Profile')
    def test_reading_profile_delegates_to_profile_class(self, profile_instance):
        base_dir = self.create_temp_config_dir(self.SINGLE_PROFILE_NO_CONFIG_DIR)
        profile_manager = ProfileManager(base_dir=base_dir)
        expected_profile_path = PurePath.joinpath(Path(profile_manager.config_dir),
                                                  'test_profile2.yml')

        actual_profile = profile_manager.read("test_profile2")

        profile_instance.assert_called_with(expected_profile_path)
        self.assertEqual(profile_instance.return_value, actual_profile)


    # delete() test

    @patch('conjur.profile_manager.Profile')
    def test_deleting_profile_delegates_to_profile_class(self, profile_instance):
        base_dir = self.create_temp_config_dir(self.SINGLE_PROFILE_NO_CONFIG_DIR)
        profile_manager = ProfileManager(base_dir=base_dir)
        expected_profile_path = PurePath.joinpath(Path(profile_manager.config_dir),
                                                  'test_profile2.yml')

        profile_manager.delete("test_profile2")

        profile_instance.assert_called_with(expected_profile_path)
        profile_instance.return_value.delete.assert_called()
