# -*- coding: utf-8 -*-

"""
API module

Provides high-level interface for programmatic API interactions
"""

import json
import logging

from datetime import datetime, timedelta

from .endpoints import ConjurEndpoint
from .http import HttpVerb, invoke_endpoint


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

        if not ssl_verify:
            logging.warning("*" * 60)
            logging.warning("'ssl_verify' is False - YOU ARE VULNERABLE TO MITM ATTACKS!")
            logging.warning("*" * 60)

            # pylint: disable=import-outside-toplevel
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # WARNING: ONLY FOR DEBUGGING - DO NOT CHECK IN LINES BELOW UNCOMMENTED
        # from .http import enable_http_logging
        # if http_debug: enable_http_logging()

        # Sanity checks
        if not self._url:
            raise Exception("ERROR: API instantiation parameter 'url' cannot be empty!")

    @property
    # pylint: disable=missing-docstring
    def api_token(self):
        if not self._api_token or datetime.now() > self.api_token_expiration:
            logging.info("API token missing or expired. Fetching new one...")
            self.api_token_expiration = datetime.now() + timedelta(minutes=self.API_TOKEN_DURATION)
            self._api_token = self.authenticate()
            return self._api_token

        logging.info("Using cached API token...")
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

        logging.info("Logging in to %s...", self._url)
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

        logging.info("Authenticating to %s...", self._url)
        return invoke_endpoint(HttpVerb.POST, ConjurEndpoint.AUTHENTICATE, params,
                               self.api_key, ssl_verify=self._ssl_verify).text

    def list_resources(self):
        """
        This method is used to fetch all available resources for the current
        account. Results are returned as an array of identifiers.
        """
        params = {
            'account': self._account
        }
        params.update(self._default_params)

        json_response = invoke_endpoint(HttpVerb.GET, ConjurEndpoint.RESOURCES,
                                        params,
                                        api_token=self.api_token,
                                        ssl_verify=self._ssl_verify).content

        resources = json.loads(json_response.decode('utf-8'))
        resource_list = map(lambda resource: resource['id'], resources)

        return list(resource_list)

    def get_variable(self, variable_id):
        """
        This method is used to fetch a secret's (aka "variable") value from
        Conjur vault.
        """

        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': variable_id,
        }
        params.update(self._default_params)

        return invoke_endpoint(HttpVerb.GET, ConjurEndpoint.SECRETS, params,
                               api_token=self.api_token, ssl_verify=self._ssl_verify).content

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
        This method is used to load, replace or delete a file-based policy into the desired
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

    def apply_policy_file(self, policy_id, policy_file):
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

    def delete_policy_file(self, policy_id, policy_file):
        """
        This method is used to delete a file-based policy into the desired
        policy ID.
        """

        return self._load_policy_file(policy_id, policy_file, HttpVerb.PATCH)

    def whoami(self):
        """
        This method provides dictionary of information about the user making an API request.
        """
        json_response = invoke_endpoint(HttpVerb.GET, ConjurEndpoint.WHOAMI,
                                        self._default_params,
                                        api_token=self.api_token,
                                        ssl_verify=self._ssl_verify).content

        return json.loads(json_response.decode('utf-8'))
