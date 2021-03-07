from pathlib import Path

# Internals
from conjur.constants import *


class TestRunnerPathProvider():  # pragma: no cover
    """
    used to generate the files path's in all tests
    in particular this file is helping with the
    integration between running test_integration script
    and the integration_test_runner. all test path's
    should go through here. in the future should use
    the constants module to be more stable. we use abstract
    class so that every enviornment could easily setup it's own files structure.
    """
    __instance = None

    @staticmethod
    def getInstance():
        """
        Implement the singelton design pattern. so we will be sure all path's are stable
        @return:  TestPathProvider
        """
        if TestRunnerPathProvider.__instance is None:
            TestRunnerPathProvider()
        return TestRunnerPathProvider.__instance

    def __init__(self, root_dir=None, file_helper_dir=None):
        if TestRunnerPathProvider.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            TestRunnerPathProvider.__instance = self

        if root_dir:
            self.ROOT_DIR = root_dir
        else:
            self.ROOT_DIR = Path.home()

        if file_helper_dir:
            self.HELPERS_FILES_DIR = file_helper_dir
        else:
            self.HELPERS_FILES_DIR = './test'

    @property
    def conjurrc_path(self):
        return os.path.join(self.ROOT_DIR, self.conjurrc_file_name)

    @property
    def test_missing_account_conjurrc(self):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", "missing_account_conjurrc")

    @property
    def test_insecure_conjurrc_file_path(self):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", "no_cert_conjurrc")

    @property
    def netrc_path(self):
        return os.path.join(self.ROOT_DIR, self.netrc_file_name)

    @property
    def cert_file_path(self):
        return os.path.join(self.ROOT_DIR, self.cert_file_name)

    @property
    def conjurrc_file_name(self):
        return '.conjurrc'

    @property
    def test_conjurrc_file_path(self):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", "conjurrc")

    @property
    def netrc_file_name(self):
        return DEFAULT_NETRC_FILE_NAME

    @property
    def cert_file_name(self):
        return 'conjur-server.pem'

    @property
    def helpers_files_path(self):
        return self.HELPERS_FILES_DIR

    @property
    def nginx_conf_path(self):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", "https", "nginx.conf")

    @property
    def certificate_path(self):
        return os.path.join(self.ROOT_DIR, self.cert_file_name)

    def get_policy_path(self, type: str):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", f"{type}_policy.yml")
