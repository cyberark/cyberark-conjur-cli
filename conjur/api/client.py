# -*- coding: utf-8 -*-

"""
Client module

This module is used to setup an API client that will be used fo interactions with
the Conjur server
"""

# Builtins
import json
import logging
from typing import Optional

# Internals
from conjur.data_object.create_host_data import CreateHostData
from conjur.data_object.create_token_data import CreateTokenData
from conjur.data_object.list_members_of_data import ListMembersOfData
from conjur.data_object.list_permitted_roles_data import ListPermittedRolesData
from conjur.errors import CertificateVerificationException, ConfigurationMissingException, \
    InvalidConfigurationException, ResourceNotFoundException, MissingRequiredParameterException
from conjur.logic.credential_provider.credential_store_factory import CredentialStoreFactory
from conjur.util import util_functions
from conjur.api import Api
from conjur.config import Config as ApiConfig
from conjur.resource import Resource

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
class Client:
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
                 account: str = None,
                 api_key: str = None,
                 ca_bundle: str = None,
                 debug: bool = False,
                 http_debug=False,
                 login_id: str = None,
                 password: str = None,
                 ssl_verify: bool = True,
                 url: str = None):

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
                raise CertificateVerificationException(
                    cause="The client was initialized without certificate verification, "
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
            credential_provider = CredentialStoreFactory.create_credential_store()
            credential_location = credential_provider.get_store_location()
            logging.debug(f"Attempting to retrieve credentials from the '{credential_location}'...")
            loaded_credentials = credential_provider.load(loaded_config['url'])
            logging.debug(f"Successfully retrieved credentials from the '{credential_location}'")

            self._api = Api(http_debug=http_debug,
                            ssl_verify=ssl_verify,
                            login_id=loaded_credentials.login,
                            api_key=loaded_credentials.password,
                            **loaded_config)

        logging.debug("Client initialized")

    @classmethod
    def setup_logging(cls, debug: bool):
        """
        Configures the logging for the client
        """
        # Suppress third party logs

        if debug:
            logging.basicConfig(level=logging.DEBUG, format=cls.LOGGING_FORMAT)
        else:
            logging.basicConfig(level=logging.WARN, format=cls.LOGGING_FORMAT_WARNING)

    ### API passthrough

    def whoami(self) -> dict:
        """
        Provides dictionary of information about the user making an API request
        """
        return self._api.whoami()

    # Constraints remain an optional parameter for backwards compatibility in the SDK
    def list(self, list_constraints: dict = None) -> dict:
        """
        Lists all available resources
        """
        return self._api.resources_list(list_constraints)

    def list_permitted_roles(self, list_permitted_roles_data: ListPermittedRolesData) -> dict:
        """
        Lists the roles which have the named permission on a resource.
        """
        return self._api.list_permitted_roles(list_permitted_roles_data)

    def list_members_of_role(self, data: ListMembersOfData) -> dict:
        """
        Lists the roles which have the named permission on a resource.
        """
        return self._api.list_members_of_role(data)

    def get(self, variable_id: str, version: str = None) -> Optional[bytes]:
        """
        Gets a variable value based on its ID
        """
        return self._api.get_variable(variable_id, version)

    def get_many(self, *variable_ids) -> Optional[bytes]:
        """
        Gets multiple variable values based on their IDs. Returns a
        dictionary of mapped values.
        """
        return self._api.get_variables(*variable_ids)

    def create_token(self, create_token_data: CreateTokenData) -> json:
        """
        Create token/s for hosts with restrictions
        """
        return self._api.create_token(create_token_data).json()

    def create_host(self, create_host_data: CreateHostData) -> json:
        """
        Create host using the hostfactory
        """
        return self._api.create_host(create_host_data).json()

    def revoke_token(self, token: str) -> int:
        """
        Revokes the given token
        """
        return self._api.revoke_token(token).status_code

    def set(self, variable_id: str, value: str) -> str:
        """
        Sets a variable to a specific value based on its ID
        """
        self._api.set_variable(variable_id, value)

    def load_policy_file(self, policy_name: str, policy_file: str) -> dict:
        """
        Applies a file-based policy to the Conjur instance
        """
        return self._api.load_policy_file(policy_name, policy_file)

    def replace_policy_file(self, policy_name: str, policy_file: str) -> dict:
        """
        Replaces a file-based policy defined in the Conjur instance
        """
        return self._api.replace_policy_file(policy_name, policy_file)

    def update_policy_file(self, policy_name: str, policy_file: str) -> dict:
        """
        Replaces a file-based policy defined in the Conjur instance
        """
        return self._api.update_policy_file(policy_name, policy_file)

    def rotate_other_api_key(self, resource: Resource) -> str:
        """
        Rotates a API keys and returns new API key
        """
        return self._api.rotate_other_api_key(resource)

    def rotate_personal_api_key(self, logged_in_user: str, current_password: str) -> str:
        """
        Rotates personal API keys and returns new API key
        """
        return self._api.rotate_personal_api_key(logged_in_user, current_password)

    def change_personal_password(self, logged_in_user: str, current_password: str,
                                 new_password: str) -> str:
        """
        Change personal password of logged-in user
        """
        # pylint: disable=line-too-long
        return self._api.change_personal_password(logged_in_user, current_password, new_password)

    def find_resources_by_identifier(self, resource_identifier: str) -> list:
        """
        Get all the resources with the given identifier.
        """
        list_constraints = {"search": resource_identifier}
        returned_resources_ids = self.list(list_constraints)

        def get_resource_kind_if_matches(returned_resource_id):
            resource = Resource.from_full_id(returned_resource_id)
            return resource if resource.identifier == resource_identifier else None

        resources = map(get_resource_kind_if_matches, returned_resources_ids)
        resources = [res for res in resources if res]  # Remove None elements
        return resources

    def find_resource_by_identifier(self, resource_identifier: str) -> list:
        """
        Look for a resource with the given identifier, and return its kind.
        Fail if there isn't exactly one such resource.
        """
        resources = self.find_resources_by_identifier(resource_identifier)
        if not resources:
            raise ResourceNotFoundException(resource_identifier)
        if len(resources) > 1:
            raise MissingRequiredParameterException(
                f"Ambiguous resource identifier: {resource_identifier}. "
                f"There are multiple resources with this identifier: "
                f"({', '.join([res.full_id() for res in resources])})")

        return resources[0]
