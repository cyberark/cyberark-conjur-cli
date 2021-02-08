# CLI Refactor

The purpose of this document is to outline the parts of the Python CLI/SDK code that we would like to refactor as well as provide a design for each. After this, we hope that the code will be more readable and easier to contribute to and maintain.

### Table of Contents

* [Organize directory structure](#organize-directory-structure)
    - [Proposal](#proposal)
    - [Current State](#current-state)
    - [Recommendation](#recommendation)
* [Improve Error Handling](#improve-error-handling)
    - [Proposal](#proposal-1)
    - [Current state](#current-state)
    - [Recommendation](#recommendation-1)
* [Strong-type function parameters and return types](#strong-type-function-parameters-and-return-types)
    - [Proposal](#proposal-2)
    - [Current state](#current-state-1)
    - [Recommendation](#recommendation-2)
* [Explicit Import Statements](#explicit-import-statements)
    - [Proposal](#proposal-3)
    - [Current state](#current-state-2)
    - [Recommendation](#recommendation-3)

- [APPENDIX](#appendix)
  * [APPENDIX 1: Error Handling](#appendix-1--error-handling)



### Organize directory structure

##### Proposal

Update the new current directory structure so that it is divided by the types of files and their responsibilities. For example, all `Controller` classes will be placed in a single directory.

##### Current State

Currently, the directory structure resembles the following:

| Directory Name | Purpose                           |
| :------------- | :-------------------------------- |
| host           | Files related to host command     |
| init           | Files related to init command     |
| list           | Files related to list command     |
| login          | Files related to login command    |
| logout         | Files related to logout command   |
| policy         | Files related to policy command   |
| user           | Files related to user command     |
| variable       | Files related to variable command |

The following files are without parent directories: api.py, client.py, argparse_wrapper.py, cli.py , client.py, config.py, constants.py, credentials_data.py, credentials_from_file.py, endpoint.py, errors.py, http_wrapper.py, resource.py, ssl_service.py, version.py

##### Recommendation

The files need to be organized by their types and not by the commands they represent.

| Directory Name | Purpose                                                      |
| :------------- | :----------------------------------------------------------- |
| wrappers       | Wrappers and utils of different Python libraries:  `arg_parse_wrapper`, `http_wrapper` |
| conjur_api     | Files that communicate directly to Conjur. For example,  `client.py , api.py, ssl_client.py (ssl_service)` |
| logic          | All logic classes                                            |
| controller     | All controller classes                                       |
| logic          | All logic classes                                            |
| data_objects   | All data objects classes                                     |



### Improve Error Handling

##### Proposal

Improve our error handling to catch our own Conjur-CLI/SDK specific objects and not general exceptions that do not provide troubleshooting information to the end user.

##### Current state

In the codebase, there are general errors that are not representative of the actual error that took place. For example, in the following `get_certificate` function a general Exception is being raised if anything goes wrong during the certificate retrieval operation. We should evaluate the types of exceptions that can be returned and create our own exception objects.

Additionally, raised exceptions are not documented in the docstring of functions.

```python
def get_certificate(self, hostname, port):
    """
    Method for connecting to Conjur to fetch the certificate chain
    """
    if port is None:
        port = DEFAULT_PORT
    try:
        fingerprint, readable_certificate = self.ssl_service.get_certificate(hostname, port)
        logging.debug("Successfully fetched certificate")
    except Exception as error:
        raise Exception(f"Unable to retrieve certificate from {hostname}:{port}. " \
                        f"Reason: {str(error)}") from error

    return fingerprint, readable_certificate
```

##### Recommendation

Map current error and exception handling and create Conjur CLI/SDK-specific exceptions and add the types of exceptions that can be raised in the function's docstring. The code block above should be:

```python
    def get_certificate(self, hostname, port):
        """
        Method for connecting to Conjur to fetch the certificate chain
        :raises CertificateRetrievalFails when certificate retrivial failes
        """
        if port is None:
            port = DEFAULT_PORT
        try:
            fingerprint, readable_certificate = self.ssl_service.get_certificate(hostname, port)
            logging.debug("Successfully fetched certificate")
        except Exception as error:
            raise CertificateRetrievalFailedException(f"Unable to retrieve certificate from {hostname}:{port}. "
                            f"Reason: {str(error)}") from error

        return fingerprint, readable_certificate
```

See [APPENDIX 1](#appendix) for a full list for all raised exceptions that we can plan on changing.



### Strong-type function parameters and return types

##### Proposal

Strong-type all parameters and function return types as per Python3 best practices.

##### Current state

Functions are not strongly typed. For example, `def get_variable(self, variable_data):` in `api.py`

##### Recommendation

Strong type functions so they will resemble `def get_variable(self, variable_data : VariableData) -> str:`



### Explicit Import Statements

##### Proposal

Ensure all import statements are explicit and contain full path. Explicit paths make it easier to tell exactly what the imported resource is and which module it is a part of. Additionally, absolute imports remain valid even if the location of the imported resources changes.

##### Current state

The codebase contains implicit import statements.

```python
from .client import Client
```

##### Recommendation

Use explicit import statements instead.

```python
from conjur.client import Client
```



## APPENDIX

### APPENDIX 1: Error Handling

The following is a mapping of builtin and third-party exceptions that are currently raised in Conjur CLI. In this section, we will provide suggestions for Conjur CLI/SDK-specific exceptions that should be raised instead of the current, general ones.

* api.py

  * `def __init__()`

    * `RuntimeError` can be replaced with `MissingParameterException`

      ```python
      self._account = account
      if not self._account:
          raise RuntimeError("Account cannot be empty!")
      ```

    * `RuntimeError` can be replaced with `MissingParameterException`

      * ```python
        self._account = account
        if not self._account:
            raise RuntimeError("Account cannot be empty!")
        ```

  * `def login()`

    * `RuntimeError` can be replaced with `MissingParameterException`

      ```python
      if not login_id or not password:
          # TODO: Use custom error
          raise RuntimeError("Missing parameters in login invocation!")
      ```

  * `def authenticate()`

    * `RuntimeError` can be replaced with `MissingParameterException`

      * ```python
        if not self.login_id or not self.api_key:
            raise RuntimeError("Missing parameters in authentication invocation!")
        ```

* `def rotate_other_api_key()`

  * `Exception` should be replaced with `InvalidResourceException`

    ```python
      if resource.type not in ('user', 'host'):
          raise Exception("Error: Invalid resource type")
      ```

* client.py

  * `def __init__()`

    ```python
    try:
        credentials = CredentialsFromFile(DEFAULT_NETRC_FILE)
        loaded_netrc = credentials.load(loaded_config['url'])
    except netrc.NetrcParseError as netrc_error:
        raise Exception("Error: netrc is in an invalid format. "
                        f"Reason: {netrc_error}") from netrc_error
    except Exception as exception:
        raise RuntimeError("Unable to authenticate with Conjur. Please log in and try again.") from exception
    ```

* `raise Exception` should be replaced with `raise ParsingCredentialsException`
    * `raise RuntimeError` should be replaced with `raise AuthenticationFailedException`


* credentials_from_file.py

  * `def load()`

    * `raise Exception` should be replaced with `raise NotLoggedInException`

      ```python
      if netrc_obj.hosts == {}:
          raise Exception("You are already logged out")
      ```

      ```python
      if netrc_auth == "":
          raise Exception("You are already logged out")
      ```

* init_controller.py

  * `def get_server_certificate()`

    * `RuntimeError` should be replaced with `MissingParameterException`

      ```python
      if self.conjurrc_data.appliance_url == '':
          raise RuntimeError("Error: URL is required")
      ```

* `RuntimeError` should be replaced with `InvalidURLFormatException`

  ```python
      if url.scheme != 'https':
          raise RuntimeError(f"Error: undefined behavior. Reason: The Conjur URL format provided "
                 f"'{self.conjurrc_data.appliance_url}' is not supported.")
      ```

* `RuntimeError` should be replaced with `ConfirmationException`

  ```python
      trust_certificate = input("Trust this certificate? (Default=no): ").strip()
      if trust_certificate.lower() != 'yes':
          raise RuntimeError("You decided not to trust the certificate")
      ```

* `def get_account_info()`

  * `RuntimeError` should be replaced with `MissingParameterException`

    ```python
      try:
          self.init_logic.fetch_account_from_server(self.conjurrc_data)
      except Exception as error:
          logging.warning(f"Unable to fetch the account from the Conjur server. Reason: {error}")
          conjurrc_data.account = input("Enter the Conjur account name (required): ").strip()

          if conjurrc_data.account is None or conjurrc_data.account == '':
              raise RuntimeError("Error: account is required")
      ```

  * `def __ensure_overwrite_file()`

    * `Exception` should be replaced with `ConfirmationException`

    ```python
      force_overwrite = input(f"File {config_file} exists. " \
                            f"Overwrite? (Default=yes): ").strip()
      if force_overwrite != '' and force_overwrite.lower() != 'yes':
        raise Exception(f"Not overwriting {config_file}")
      ```

* init_logic.py

  * `def get_certificate()`

    * `Exception` should be replaced with `FailedToRetrieveCertificateException`

    *  The following are error can be thrown from `ssl_service.get_certificate` :

      * `TIMEOUT_ERROR` when connection to server fails
      * `socket.gaierror` when there is no such DNS address

      ```python
      try:
          fingerprint, readable_certificate = self.ssl_service.get_certificate(hostname, port)
          logging.debug("Successfully fetched certificate")
      except Exception as error:
          raise Exception(f"Unable to retrieve certificate from {hostname}:{port}. " \
                          f"Reason: {str(error)}") from error
      ```

* login_controller.py

  * `def get_username()`

    * `RuntimeError` should be replaced with `MissingRequiredParameterException`

      ```python
      self.credential_data.login = input("Enter your login name to log into Conjur: ").strip()
      if self.credential_data.login == '':
          # pylint: disable=raise-missing-from
          raise RuntimeError("Error: Login name is required")
      ```

  * `def get_api_key()`

    * `RuntimeError` should be replaced with `AuthenticationFailedException`

      ```python
      try:
          self.credential_data.api_key = self.login_logic.get_api_key(self.ssl_verify,
                                                         self.credential_data,
                                                         self.user_password,
                                                         conjurrc)
      except Exception as error:
          raise RuntimeError("Failed to log in to Conjur. Unable to authenticate with Conjur. " \
              f"Reason: {error}. Check your credentials and try again.") from error
      ```

* logout_controller.py

  * `def remove_credentials()`

    ```python
    logging.debug("Attempting to log out of Conjur")
    try:
        if not os.path.exists(DEFAULT_NETRC_FILE):
            sys.stdout.write("Successfully logged out from Conjur.\n")
        elif os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0:
            conjurrc = ConjurrcData.load_from_file(DEFAULT_CONFIG_FILE)
            self.logout_logic.remove_credentials(conjurrc.appliance_url)
            logging.debug("Logout successful")
            sys.stdout.write("Successfully logged out from Conjur.\n")
        else:
            raise Exception("You are already logged out")
    except Exception as error:
        # pylint: disable=raise-missing-from
        raise Exception(f"Failed to log out. {error}.")
    ```

    * First exception should raise `NotLoggedInException`
    * Second Exception shoud be `LoggedOutFailedException`
