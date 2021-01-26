# -*- coding: utf-8 -*-

"""
API module

Provides high-level interface for programmatic API interactions
"""
# Builtins
import json
import logging

# Third party
from datetime import datetime, timedelta

# Internals
from conjur.endpoints import ConjurEndpoint
from conjur.http_wrapper import HttpVerb, invoke_endpoint


# pylint: disable=too-many-instance-attributes
class Api():
    """
    This module provides a high-level programmatic access to the HTTP API
    when all the needed arguments and parameters are well-known
    """

    # Tokens should only be reused for 5 minutes (max lifetime is 8 minutes)
    API_TOKEN_DURATION = 5

    KIND_VARIABLE = 'variable'
    SECRET_ID_FORMAT = '{account}:{kind}:{id}'
    SECRET_ID_RETURN_PREFIX = '{account}:{kind}:'

    _api_token = None

    # We explicitly want to enumerate all params needed to instantiate this
    # class but this might not be needed in the future
    # pylint: disable=unused-argument,too-many-arguments
    def __init__(self,
                 account='default',
                 api_key=None,
                 ca_bundle=None,
                 http_debug=False,
                 login_id=None,
                 plugins=None,
                 ssl_verify=True,
                 url=None):

        self._url = url
        self._ca_bundle = ca_bundle

        self._account = account
        if not self._account:
            raise RuntimeError("Account cannot be empty!")

        self._ssl_verify = ssl_verify
        if ca_bundle:
            self._ssl_verify = ca_bundle

        self.api_key = api_key
        self.login_id = login_id

        self.api_token_expiration = None

        self._default_params = {
            'url': url,
            'account': account
        }

        # WARNING: ONLY FOR DEBUGGING - DO NOT CHECK IN LINES BELOW UNCOMMENTED
        # from .http import enable_http_logging
        # if http_debug: enable_http_logging()

        # Sanity checks
        if not self._url:
            raise Exception("Error: API instantiation parameter 'url' cannot be empty!")

    @property
    # pylint: disable=missing-docstring
    def api_token(self):
        if not self._api_token or datetime.now() > self.api_token_expiration:
            logging.debug("API token missing or expired. Fetching new one...")
            self.api_token_expiration = datetime.now() + timedelta(minutes=self.API_TOKEN_DURATION)
            self._api_token = self.authenticate()

            return self._api_token

        logging.debug("Using cached API token...")
        return self._api_token

    def login(self, login_id=None, password=None):
        """
        This method uses the basic auth login id (username) and password
        to retrieve an api key from the server that can be later used to
        retrieve short-lived api tokens.
        """

        if not login_id or not password:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in login invocation!")

        logging.debug("Logging in to %s...", self._url)
        self.api_key = invoke_endpoint(HttpVerb.GET, ConjurEndpoint.LOGIN,
                                       self._default_params, auth=(login_id, password),
                                       ssl_verify=self._ssl_verify).text
        self.login_id = login_id

        return self.api_key

    def authenticate(self):
        """
        Authenticate uses the api_key to fetch a short-lived api token that
        for a limited time will allow you to interact fully with the Conjur
        vault.
        """
        if not self.login_id or not self.api_key:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in authentication invocation!")

        params = {
            'login': self.login_id
        }
        params.update(self._default_params)

        logging.debug("Authenticating to %s...", self._url)
        return invoke_endpoint(HttpVerb.POST, ConjurEndpoint.AUTHENTICATE, params,
                               self.api_key, ssl_verify=self._ssl_verify).text

    def resources_list(self, list_constraints=None):
        """
        This method is used to fetch all available resources for the current
        account. Results are returned as an array of identifiers.
        """
        params = {
            'account': self._account
        }
        params.update(self._default_params)
        if list_constraints is not None:
            json_response = invoke_endpoint(HttpVerb.GET, ConjurEndpoint.RESOURCES,
                                            params,
                                            query=list_constraints,
                                            api_token=self.api_token,
                                            ssl_verify=self._ssl_verify).content
        else:
            json_response = invoke_endpoint(HttpVerb.GET, ConjurEndpoint.RESOURCES,
                                params,
                                api_token=self.api_token,
                                ssl_verify=self._ssl_verify).content

        resources = json.loads(json_response.decode('utf-8'))

        # Returns the result as a list of resource ids instead of the raw JSON only
        # when the user does not provide `inspect` as one of their filters
        if list_constraints is not None and 'inspect' not in list_constraints:
            # For each element (resource) in the resources sequence, we extract the resource id
            resource_list = map(lambda resource: resource['id'], resources)
            return list(resource_list)

        # To see the full resources response see
        # https://docs.conjur.org/Latest/en/Content/Developer/Conjur_API_List_Resources.htm?tocpath=Developer%7CREST%C2%A0APIs%7C_____17
        return resources

    def get_variable(self, variable_id, version=None):
        """
        This method is used to fetch a secret's (aka "variable") value from
        Conjur vault.
        """
        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': variable_id,
        }
        params.update(self._default_params)

        query_params = {}
        if version is not None:
            query_params = {
                'version': version
            }

        # pylint: disable=no-else-return
        if version is not None:
            return invoke_endpoint(HttpVerb.GET, ConjurEndpoint.SECRETS, params,
                                   api_token=self.api_token, query=query_params,
                                   ssl_verify=self._ssl_verify).content
        else:
            return invoke_endpoint(HttpVerb.GET, ConjurEndpoint.SECRETS, params,
                                   api_token=self.api_token,
                                   ssl_verify=self._ssl_verify).content

    def get_variables(self, *variable_ids):
        """
        This method is used to fetch multiple secret's (aka "variable") values from
        Conjur vault.
        """
        assert variable_ids, 'Variable IDs must not be empty!'

        full_variable_ids = []
        for variable_id in variable_ids:
            full_variable_ids.append(self.SECRET_ID_FORMAT.format(account=self._account,
                                                                  kind=self.KIND_VARIABLE,
                                                                  id=variable_id))
        query_params = {
            'variable_ids': ','.join(full_variable_ids),
        }

        json_response = invoke_endpoint(HttpVerb.GET, ConjurEndpoint.BATCH_SECRETS,
                                        self._default_params,
                                        api_token=self.api_token,
                                        ssl_verify=self._ssl_verify,
                                        query=query_params,
                                        ).content

        variable_map = json.loads(json_response.decode('utf-8'))

        # Remove the 'account:variable:' prefix from result's variable names
        remapped_keys_dict = {}
        prefix_length = len(self.SECRET_ID_RETURN_PREFIX.format(account=self._account,
                                                                kind=self.KIND_VARIABLE))
        for variable_name, variable_value in variable_map.items():
            new_variable_name = variable_name[prefix_length:]
            remapped_keys_dict[new_variable_name] = variable_value

        return remapped_keys_dict

    def set_variable(self, variable_id, value):
        """
        This method is used to set a secret (aka "variable") to a value of
        your choosing.
        """

        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': variable_id,
        }
        params.update(self._default_params)

        return invoke_endpoint(HttpVerb.POST, ConjurEndpoint.SECRETS, params,
                               value, api_token=self.api_token,
                               ssl_verify=self._ssl_verify).text

    def _load_policy_file(self, policy_id, policy_file, http_verb):
        """
        This method is used to load, replace or update a file-based policy into the desired
        name.
        """

        params = {
            'identifier': policy_id,
        }
        params.update(self._default_params)

        policy_data = None
        with open(policy_file, 'r') as content_file:
            policy_data = content_file.read()

        json_response = invoke_endpoint(http_verb, ConjurEndpoint.POLICIES, params,
                                        policy_data, api_token=self.api_token,
                                        ssl_verify=self._ssl_verify).text

        policy_changes = json.loads(json_response)
        return policy_changes

    def load_policy_file(self, policy_id, policy_file):
        """
        This method is used to load a file-based policy into the desired
        name.
        """

        return self._load_policy_file(policy_id, policy_file, HttpVerb.POST)

    def replace_policy_file(self, policy_id, policy_file):
        """
        This method is used to replace a file-based policy into the desired
        policy ID.
        """

        return self._load_policy_file(policy_id, policy_file, HttpVerb.PUT)

    def update_policy_file(self, policy_id, policy_file):
        """
        This method is used to update a file-based policy into the desired
        policy ID.
        """

        return self._load_policy_file(policy_id, policy_file, HttpVerb.PATCH)

    def rotate_other_api_key(self, resource_obj):
        """
        This method is used to rotate a user/host's API key that is not the current user.
        To rotate API key of the current user use rotate_personal_api_key
        """
        if resource_obj.resource_type not in ('user', 'host'):
            raise Exception("Error: Invalid resource type")

        # Attach the resource type (user or host)
        query_params = {
            'role': resource_obj.full_id()
        }
        response = invoke_endpoint(HttpVerb.PUT, ConjurEndpoint.ROTATE_API_KEY,
                                   self._default_params,
                                   api_token=self.api_token,
                                   ssl_verify=self._ssl_verify,
                                   query=query_params).text
        return response

    def rotate_personal_api_key(self, logged_in_user, current_password):
        """
        This method is used to rotate a personal API key
        """
        response = invoke_endpoint(HttpVerb.PUT, ConjurEndpoint.ROTATE_API_KEY,
                                   self._default_params,
                                   api_token=self.api_token,
                                   auth=(logged_in_user, current_password),
                                   ssl_verify=self._ssl_verify).text
        return response

    def change_personal_password(self, logged_in_user, current_password, new_password):
        """
        This method is used to change own password
        """
        response = invoke_endpoint(HttpVerb.PUT, ConjurEndpoint.CHANGE_PASSWORD,
                                   self._default_params,
                                   new_password,
                                   api_token=self.api_token,
                                   auth=(logged_in_user, current_password),
                                   ssl_verify=self._ssl_verify
                                   ).text
        return response

    def whoami(self):
        """
        This method provides dictionary of information about the user making an API request.
        """
        json_response = invoke_endpoint(HttpVerb.GET, ConjurEndpoint.WHOAMI,
                                        self._default_params,
                                        api_token=self.api_token,
                                        ssl_verify=self._ssl_verify).content

        return json.loads(json_response.decode('utf-8'))
