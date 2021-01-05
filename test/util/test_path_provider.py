import os
from pathlib import Path
from abc import ABC, abstractmethod

# Internals
from conjur.constants import *


class TestPathProviderBase(ABC):  # pragma: no cover
    """
    used to generate the files path's in all tests
    in particular this file is helping with the
    integration between running test_integration script
    and the integration_test_runner. all test path's
    should go through here. in the future should use
    the constants module to be more stable. we use abstract
    class so that every enviorment could easily setup it's own files structure.
    """

    def __init__(self, root_dir, file_helper_dir):
        self.ROOT_DIR = root_dir
        self.HELPERS_FILES_DIR = file_helper_dir

    @property
    def conjurrc_path(self):
        return os.path.join(self.ROOT_DIR, self.conjurrc_file_name)

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
    @abstractmethod
    def test_conjurrc_file_path(self):
        raise NotImplemented()

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
    @abstractmethod
    def nginx_conf_path(self):
        raise NotImplemented()

    @property
    @abstractmethod
    def certificate_path(self):
        raise NotImplemented()

    @abstractmethod
    def get_policy_path(self, type: str):
        raise NotImplemented()


class TestRunnerPathProvider(TestPathProviderBase):  # pragma: no cover
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

    def __init__(self, root_dir=None, helpers_file_dir=None, force_override=False):
        super(TestRunnerPathProvider, self).__init__(None, None)
        root_dir_env = Path.home()
        helpers_file_env = './test'

        if not root_dir:
            self.ROOT_DIR = root_dir_env
        else:
            self.ROOT_DIR = root_dir

        if not helpers_file_dir:
            self.HELPERS_FILES_DIR = helpers_file_env
        else:
            self.HELPERS_FILES_DIR = helpers_file_dir

        if TestRunnerPathProvider.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            TestRunnerPathProvider.__instance = self

    @property
    def test_conjurrc_file_path(self):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", "conjurrc")

    @property
    def test_no_cert_conjurrc_file_path(self):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", "no_cert_conjurrc")

    @property
    def test_bad_cert_conjurrc_file_path(self):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", "bad_cert_conjurrc")

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


class TestIntegrationPathProvider(TestPathProviderBase):  # pragma: no cover
    """
    used to generate the files path's in all tests
    in particular this file is helping with the
    integration between running test_integration script
    and the integration_test_runner.all test path's
    should go through here. in the future should
    use the constants module to be more stable
    """
    __instance = None

    @staticmethod
    def getInstance():
        """
        Implement the singelton design pattern. so we will be sure all path's are stable
        @return:  TestPathProvider
        """

        if TestIntegrationPathProvider.__instance is None:
            TestIntegrationPathProvider()
        return TestIntegrationPathProvider.__instance

    def __init__(self):
        super(TestIntegrationPathProvider, self).__init__(Path.home(), './test')

        if TestIntegrationPathProvider.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            TestIntegrationPathProvider.__instance = self

    @property
    def test_conjurrc_file_path(self):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", "conjurrc")

    @property
    def test_no_cert_conjurrc_file_path(self):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", "no_cert_conjurrc")

    @property
    def test_bad_cert_conjurrc_file_path(self):
        return os.path.join(self.HELPERS_FILES_DIR, "test_config", "bad_cert_conjurrc")

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
