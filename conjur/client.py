# -*- coding: utf-8 -*-

"""
Client module

This module is used to setup an API client that will be used fo interactions with
the Conjur server
"""

# Builtins
import logging

# Internals
import netrc

from Utils.utils import Utils
from conjur.api import Api
from conjur.config import Config as ApiConfig
from conjur.constants import DEFAULT_NETRC_FILE
from conjur.init.init_controller import InitController
from conjur.init.init_logic import InitLogic
from conjur.init.conjurrc_data import ConjurrcData
from conjur.credentials_from_file import CredentialsFromFile
from conjur.ssl_service import SSLService

class ConfigException(Exception):
    """
    ConfigException

    This class is used to wrap a regular exception with a more-descriptive class name

    *************** DEVELOPER NOTE ***************
    For backwards capability purposes, do not remove existing functionality
    in this class or remove params from the constructor. Although via
    the CLI we do not support commandline arguments, other developers
    use these parameters defined in this class to initialize our Python
    SDK in their code.
    """
class Client():
    """
    Client

    This class is used to construct a client for API interaction
    """
    _api = None
    _login_id = None
    _api_key = None

    LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s'

    # The method signature is long but we want to explicitly control
    # what parameters are allowed
    # pylint: disable=too-many-arguments,too-many-locals
    def __init__(self,
                 account=None,
                 api_key=None,
                 ca_bundle=None,
                 debug=False,
                 http_debug=False,
                 login_id=None,
                 password=None,
                 ssl_verify=True,
                 url=None):

        if ssl_verify is False:
            Utils.get_insecure_warning()

        self.setup_logging(debug)

        logging.debug("Initializing configuration...")

        self._login_id = login_id

        loaded_config = {
            'url': url,
            'account': account,
            'ca_bundle': ca_bundle,
        }
        if not url or not login_id or (not password and not api_key):
            try:
                on_disk_config = dict(ApiConfig())

                # We want to retain any overrides that the user provided from params
                # but only if those values are valid
                for field_name, field_value in loaded_config.items():
                    if field_value:
                        on_disk_config[field_name] = field_value
                loaded_config = on_disk_config
                # pylint: disable=logging-fstring-interpolation
                logging.debug("Fetched connection details: "
                              f"{{'account': {loaded_config['account']}, "
                              f"'appliance_url': {loaded_config['url']}, "
                              f"'cert_file': {loaded_config['ca_bundle']}}}")

            # TODO add error handling for when conjurrc field doesn't exist
            except Exception as exc:
                raise ConfigException(exc) from exc

        # We only want to override missing account info with "default"
        # if we can't find it anywhere else.
        if loaded_config['account'] is None:
            loaded_config['account'] = "default"

        if api_key:
            logging.debug("Using API key from parameters...")
            self._api = Api(api_key=api_key,
                            http_debug=http_debug,
                            login_id=login_id,
                            ssl_verify=ssl_verify,
                            **loaded_config)
        elif password:
            logging.debug("Creating API key with login ID/password combo...")
            self._api = Api(http_debug=http_debug,
                            ssl_verify=ssl_verify,
                            **loaded_config)
            self._api.login(login_id, password)
        else:
            try:
                credentials = CredentialsFromFile(DEFAULT_NETRC_FILE)
                loaded_netrc = credentials.load(loaded_config['url'])
            except netrc.NetrcParseError as netrc_error:
                raise Exception("Error: netrc is in an invalid format. " \
                                f"Reason: {netrc_error}") from netrc_error
            except Exception as exception:
                # pylint: disable=line-too-long
                raise RuntimeError("Unable to authenticate with Conjur. Please log in and try again") from exception

            self._api = Api(http_debug=http_debug,
                            ssl_verify=ssl_verify,
                            login_id=loaded_netrc['login_id'],
                            api_key=loaded_netrc['api_key'],
                            **loaded_config)

        logging.debug("Client initialized")

    def setup_logging(self, debug):
        """
        Configures the logging for the client
        """
        if debug:
            logging.basicConfig(level=logging.DEBUG, format=self.LOGGING_FORMAT)
        else:
            logging.basicConfig(level=logging.WARN, format=self.LOGGING_FORMAT)

    # Technical debt: refactor when time permits because this function
    # doesn't belong here
    @staticmethod
    def initialize(url, account, cert, force):
        """
        Initializes the client, creating the .conjurrc file
        """
        ssl_service = SSLService()

        conjurrc_data = ConjurrcData(url,
                                     account,
                                     cert)

        init_logic = InitLogic(ssl_service)

        input_controller = InitController(conjurrc_data,
                                          init_logic,
                                          force)
        input_controller.load()

    ### API passthrough

    def whoami(self):
        """
        Provides dictionary of information about the user making an API request
        """
        return self._api.whoami()

    # Constraints remain an optional parameter for backwards compatibility in the SDK
    def list(self, list_constraints=None):
        """
        Lists all available resources
        """
        return self._api.resources_list(list_constraints)

    def get(self, variable_id, version=None):
        """
        Gets a variable value based on its ID
        """
        return self._api.get_variable(variable_id, version)

    def get_many(self, *variable_ids):
        """
        Gets multiple variable values based on their IDs. Returns a
        dictionary of mapped values.
        """
        return self._api.get_variables(*variable_ids)

    def set(self, variable_id, value):
        """
        Sets a variable to a specific value based on its ID
        """
        self._api.set_variable(variable_id, value)

    def load_policy_file(self, policy_name, policy_file):
        """
        Applies a file-based policy to the Conjur instance
        """
        return self._api.load_policy_file(policy_name, policy_file)

    def replace_policy_file(self, policy_name, policy_file):
        """
        Replaces a file-based policy defined in the Conjur instance
        """
        return self._api.replace_policy_file(policy_name, policy_file)

    def update_policy_file(self, policy_name, policy_file):
        """
        Replaces a file-based policy defined in the Conjur instance
        """
        return self._api.update_policy_file(policy_name, policy_file)

    def rotate_other_api_key(self, resource, resource_to_rotate):
        """
        Rotates a API keys and returns new API key
        """
        return self._api.rotate_other_api_key(resource, resource_to_rotate)

    def rotate_personal_api_key(self, resource, logged_in_user, current_password):
        """
        Rotates personal API keys and returns new API key
        """
        return self._api.rotate_personal_api_key(resource, logged_in_user, current_password)

    def change_personal_password(self, resource, logged_in_user, current_password, new_password):
        """
        Change personal password of logged-in user
        """
        # pylint: disable=line-too-long
        return self._api.change_personal_password(resource, logged_in_user, current_password, new_password)
