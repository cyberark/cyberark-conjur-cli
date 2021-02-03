## CLI Refactor


The purpose of this document is to outline the parts of the Python CLI/SDK code that we would like to refactor as well as provide a design for each point. Through this refactor, we hope that the code will be more readable, and easier to contribute to and maintain.



### Improve Naming

------

##### Proposal

Review the names of files, functions.. and rename them to more readable names.

##### Current State

Not all the names are clear now. For example with `class Resource` it is hard to understand which resource we mean.

##### Recommendation

Go over all naming in the code and rename when need. If we rename  `class Resource` to `class ConjurResource` developer who is reading the code will understand we are referencing a specific resource, a Conjur resource. The same applies for the names of files in the repository.

### Organize directory structure

------

##### Proposal

Update the new current directory structure so that it is divided by the types of files and their responsibilities. For example, all `Controller` classes will be placed in a single directory.

##### Current State

Currently, the directory structure resembles the following

| Directory Name | Purpose                           |
| :------------- | :-------------------------------- |
| host           | files related to host command     |
| init           | files related to init command     |
| list           | files related to list command     |
| login          | files related to login command    |
| logout         | files related to logout command   |
| policy         | files related to policy command   |
| user           | files related to user command     |
| variable       | files related to variable command |

The following files are without parent directory : api.py, client.py, argparse_wrapper.py, cli.py , client.py, config.py, constants.py, credentials_data.py, credentials_form_file.py, endpoint.py, errors.py, http_wrapper.py, resource.py, ssl_service.py, version.py

##### Recommendation

I recommend that we organize the files by their types and not by the commands they represent.

| Directory Name | Purpose                                                      |
| :------------- | :----------------------------------------------------------- |
| utils          | wrappers and utils of diffrent python libs :  arg_parse_wrapper, http_wrapper |
| api            | files that talk directly with conjur. For Example   `conjur_client.py (conjur.py) , conjur_api.py (api.py), ssl_client.py (ssl_service)` |
| logics         | all logic classes                                            |
| controllers    | all controller classes                                       |
| logics         | all logic classes                                            |
| data_objects   | all data objects classes                                     |



### Improve Error Handling

------

##### Proposal

This will help to better under the error handling flow. This will allow us to catch our own object and not general exceptions that do not proper helpful information to the end user. All Conjur CLI/SDK-specific exceptions should be documented in the funtions that call them.

##### Current state

Through the codebase, we have general errors that are not representative of the actual error that took place. The exception is not documented in the fucntion documentation in the code.
For example, in the following `get_certificate` function, we raise a general exception if anything goes wrong during the certificate retrieval operation.

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

We raise Exception if anything happens in certificate retrivial.

##### Recommendation

Map current error and exception handling and create Conjur-specific exceptions. The code block above should be:

```python
    def get_certificate(self, hostname, port):
        """
        Method for connecting to Conjur to fetch the certificate chain
        :raises CertificateRetrivialFailed when certificate retrivial failes
        """
        if port is None:
            port = DEFAULT_PORT
        try:
            fingerprint, readable_certificate = self.ssl_service.get_certificate(hostname, port)
            logging.debug("Successfully fetched certificate")
        except Exception as error:
            raise CertificateRetrievalFailedException(f"Unable to retrieve certificate from {hostname}:{port}. " \
                            f"Reason: {str(error)}") from error

        return fingerprint, readable_certificate
```

Appendinx 1 lists the error handling cases where fixes need to be done.

------

### Strong-type function parameters and return types

##### Proposal

Strong-type all parameters and function return types as per Python3 best practices

##### Current state

Functions are not strongly typed.

For example, `def get_variable(self, variable_data):`

##### Recommendation

Strongly Type the function so it will resemble `def get_variable(self, variable_data : VariableData) -> str:`"

------

### Explicit Import Statements

##### Proposal

Make sure all import statement is explicit and contains full path. Explicit paths makes it easier to tell exactly what the imported resource is and where it is. Additionally, absolute imports remain valid even if the location of the imported resources changes.

##### Current state

The codebase contains implicit import statements

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

------

The following is a mapping of builtin and third-party exceptions that are currently raised in Conjur. In this document, I will provide suggestions for Conjur CLI/SDK-specific exceptions we should use instead.

* api.py

  * `def __init__()` - There are a few places that raise similar exceptions. `RuntimeError` can be replaced with `MissingParameterException`

    * Missing Account Name

      ```python
      self._account = account
      if not self._account:
          raise RuntimeError("Account cannot be empty!")
      ```

    * Missing Url

      * ```python
        self._account = account
        if not self._account:
            raise RuntimeError("Account cannot be empty!")
        ```

  * `def login()` - `RuntimeError` can be replaced with `MissingParameterException`

    * login id or password are missing 

      ```python
      if not login_id or not password:
          # TODO: Use custom error
          raise RuntimeError("Missing parameters in login invocation!")
      ```

  * `def authenticate()`

    * login id or password are missing 

      * ```python
        if not self.login_id or not self.api_key:
            # TODO: Use custom error
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
        # pylint: disable=line-too-long
        raise RuntimeError("Unable to authenticate with Conjur. Please log in and try again.") from exception
    ```

    * `raise Exception` should be replaced with `raise CredentialsParseException`
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

  * `def get_server_certificate()` function

    * `RuntimeError` should be replaced with `MissingParameterException`

      ```python
      if self.conjurrc_data.appliance_url == '':
          # pylint: disable=raise-missing-from
          raise RuntimeError("Error: URL is required")
      ```

    * `RuntimeError` should be replaced with `InvalidURLException`

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
      # pylint: disable=broad-except,logging-fstring-interpolation
      except Exception as error:
          # pylint: disable=line-too-long,logging-fstring-interpolation
          logging.warning(f"Unable to fetch the account from the Conjur server. Reason: {error}")
          # If there was a problem fetching the account from the server, we will request one
          conjurrc_data.account = input("Enter the Conjur account name (required): ").strip()
      
          if conjurrc_data.account is None or conjurrc_data.account == '':
              # pylint: disable=raise-missing-from
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

    * `RuntimeError` should be replaced with `AuthenticationException`

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