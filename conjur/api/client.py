# -*- coding: utf-8 -*-

"""
Client module

This module is used to setup an API client that will be used fo interactions with
the Conjur server
"""

# Builtins
import logging

# Internals
from conjur.logic.credential_provider.credential_store_factory import CredentialStoreFactory
from conjur.errors import CertificateVerificationException, ConfigurationMissingException, \
    InvalidConfigurationException
from conjur.util import util_functions
from conjur.api import Api
from conjur.config import Config as ApiConfig
from conjur.resource import Resource
from conjur.wrapper import KeystoreWrapper

# pylint: disable=pointless-string-statement
"""
*************** DEVELOPER NOTE ***************
For backwards capability purposes, do not remove existing functionality
in this class or remove params from the constructor. Although via
the CLI we do not support commandline arguments, other developers
use these parameters defined in this class to initialize our Python
SDK in their code.
"""

# pylint: disable=logging-fstring-interpolation,line-too-long
class Client():
    """
    Client

    This class is used to construct a client for API interaction
    """
    _api = None
    _login_id = None
    _api_key = None

    LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    LOGGING_FORMAT_WARNING = 'WARNING: %(message)s'

    # The method signature is long but we want to explicitly control
    # what parameters are allowed
    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches,line-too-long,try-except-raise,too-many-statements
    def __init__(self,
                 account:str=None,
                 api_key=None,
                 ca_bundle=None,
                 debug:bool=False,
                 http_debug=False,
                 login_id:str=None,
                 password:str=None,
                 ssl_verify:bool=True,
                 url:str=None):

        if ssl_verify is False:
            util_functions.get_insecure_warning_in_debug()

        self.setup_logging(debug)

        logging.debug("Initializing configuration...")

        self._login_id = login_id

        loaded_config = {
            'url': url,
            'account': account,
            'ca_bundle': ca_bundle,
        }
        # Parameters from initialized client are missing and
        # will try to search for them in the conjurrc
        if not url or not login_id or (not password and not api_key):
            try:
                # Loads in the conjurrc
                on_disk_config = dict(ApiConfig())
                # We want to retain any overrides that the user provided from params
                # but only if those values are valid
                for field_name, field_value in loaded_config.items():
                    if field_value:
                        on_disk_config[field_name] = field_value
                loaded_config = on_disk_config

                # Raise exception if the client was initialized with verify=False
                # but a follow-up request is run with verify=True
                if ssl_verify is True and loaded_config['ca_bundle'] == '':
                    raise CertificateVerificationException

                logging.debug("Fetched connection details: "
                              f"{{'conjur_account': {loaded_config['account']}, "
                              f"'conjur_url': {loaded_config['url']}, "
                              f"'cert_file': {loaded_config['ca_bundle']}}}")
            except CertificateVerificationException as cert_verify:
                raise CertificateVerificationException(cause="The client was initialized without certificate verification, "
                                                             "even though the command was ran with certificate verification enabled.",
                                                       solution="To continue communicating with the server insecurely, run the command "
                                                                "again with ssl_verify = False. Otherwise, reinitialize the client.") from cert_verify
            except ConfigurationMissingException as missing_config_exec:
                raise ConfigurationMissingException from missing_config_exec
            except InvalidConfigurationException as invalid_config_exec:
                raise InvalidConfigurationException from invalid_config_exec
            except Exception:
                raise

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
            credential_provider, credential_location = CredentialStoreFactory.create_credential_store()
            logging.debug(f"Attempting to retrieve credentials from the '{credential_location}'...")
            loaded_credentials = credential_provider.load(loaded_config['url'])
            logging.debug(f"Successfully retrieved credentials from the '{credential_location}'")

            self._api = Api(http_debug=http_debug,
                            ssl_verify=ssl_verify,
                            login_id=loaded_credentials.login,
                            api_key=loaded_credentials.password,
                            **loaded_config)

        logging.debug("Client initialized")

    def setup_logging(self, debug:bool):
        """
        Configures the logging for the client
        """
        # Suppress third party logs
        KeystoreWrapper.configure_keyring_log_to_info()

        if debug:
            logging.basicConfig(level=logging.DEBUG, format=self.LOGGING_FORMAT)
        else:
            logging.basicConfig(level=logging.WARN, format=self.LOGGING_FORMAT_WARNING)

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

    def get(self, variable_id:str, version:str=None):
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

    def set(self, variable_id:str, value:str):
        """
        Sets a variable to a specific value based on its ID
        """
        self._api.set_variable(variable_id, value)

    def load_policy_file(self, policy_name:str, policy_file:str):
        """
        Applies a file-based policy to the Conjur instance
        """
        return self._api.load_policy_file(policy_name, policy_file)

    def replace_policy_file(self, policy_name:str, policy_file:str):
        """
        Replaces a file-based policy defined in the Conjur instance
        """
        return self._api.replace_policy_file(policy_name, policy_file)

    def update_policy_file(self, policy_name:str, policy_file:str):
        """
        Replaces a file-based policy defined in the Conjur instance
        """
        return self._api.update_policy_file(policy_name, policy_file)

    def rotate_other_api_key(self, resource: Resource):
        """
        Rotates a API keys and returns new API key
        """
        return self._api.rotate_other_api_key(resource)

    def rotate_personal_api_key(self, logged_in_user:str, current_password:str):
        """
        Rotates personal API keys and returns new API key
        """
        return self._api.rotate_personal_api_key(logged_in_user, current_password)

    def change_personal_password(self, logged_in_user:str, current_password:str, new_password:str):
        """
        Change personal password of logged-in user
        """
        # pylint: disable=line-too-long
        return self._api.change_personal_password(logged_in_user, current_password, new_password)
