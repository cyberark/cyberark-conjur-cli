import os
from test.util.test_path_provider import TestRunnerPathProvider


class ClientParams:
    """
    DTO wrapped the client params
    Used for integration tests
    Default params are used for test_integration script
    """

    def __init__(self, url='https://conjur-https', account='dev', login='admin', api_key=None):
        self.hostname = url
        self.account = account
        self.login = login
        # when we run the tests using nose2 script we will use the CONJUR_AUTHN_API_KEY env variable
        self.env_api_key = api_key if api_key else os.environ['CONJUR_AUTHN_API_KEY']


class TestEnvironmentParams:
    """
    DTO wrapped the environmentParams params
    Used for integration tests
    Default params are used for test_integration script
    """

    def __init__(self, cli_to_test=None, invoke_process=False,
                 path_provider=None):
        self.invoke_process = invoke_process
        self.cli_to_test = cli_to_test
        if path_provider:
            self.path_provider = path_provider
        elif TestRunnerPathProvider.getInstance():
            self.path_provider = TestRunnerPathProvider.getInstance()
        else:
            self.path_provider = TestRunnerPathProvider()
