# Improve Error Handling - TODO List


This doucment maps the builtin or third party exceptino that are raised and suggest which exceptions we should use instead. It is listed by files, inside of file function and inside of function an error handling flow. In addition information from this document about reasons of why we throw these exception should be part of the relevant functions in their documentation.

* api.py

  * init function - These two exceptions can be replaced with MissingParameterException

    * EmptyParameterError Account

      ```python
      self._account = account
      if not self._account:
          raise RuntimeError("Account cannot be empty!")
      ```

    * EmptyParameterError Url

      * ```python
        self._account = account
        if not self._account:
            raise RuntimeError("Account cannot be empty!")
        ```

  * login function-

    * MissingRequiredParameterException

      ```python
      if not login_id or not password:
          # TODO: Use custom error
          raise RuntimeError("Missing parameters in login invocation!")
      ```

  * authenticate function

    * MissingRequiredParameterException

      * ```python
        if not self.login_id or not self.api_key:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in authentication invocation!")
        ```

  * rotate_other_api_key function

    * UnrotatableResource - We can rotate only user or host api key

      ```python
      if resource.type not in ('user', 'host'):
          raise Exception("Error: Invalid resource type")
      ```

* client.py

  * init function

    * CredentialsParseError

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

      About the `except Exception`  there we need to check which exception can be thrown . load functino can throw NotLogedInException (written in these document)

* credentials_from_file.py

  * load function

    * NotLogedInException

      ```python
      if netrc_obj.hosts == {}:
          raise Exception("You are already logged out")
      ```

      ```python
      if netrc_auth == "":
          raise Exception("You are already logged out")
      ```

* http_wrapper.py

  * enable_http_logging

* Init_controller.py

  * get_server_certificate function

    * EmptyParameterError

      ```python
      if self.conjurrc_data.appliance_url == '':
          # pylint: disable=raise-missing-from
          raise RuntimeError("Error: URL is required")
      ```

    * InvalidURLError

      ```python
      if url.scheme != 'https':
          raise RuntimeError(f"Error: undefined behavior. Reason: The Conjur URL format provided "
                 f"'{self.conjurrc_data.appliance_url}' is not supported.")
      ```

    * UserRefusedException - User dont trust certificate

      ```python
      trust_certificate = input("Trust this certificate? (Default=no): ").strip()
      if trust_certificate.lower() != 'yes':
          raise RuntimeError("You decided not to trust the certificate")
      ```

  * get_account_info function

    * EmptyParameterError Account

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

  * __ensure_overwrite_file function

    * UserRefusedException - User refused to overwrite the file

      ```python
      force_overwrite = input(f"File {config_file} exists. " \
                              f"Overwrite? (Default=yes): ").strip()
      if force_overwrite != '' and force_overwrite.lower() != 'yes':
          raise Exception(f"Not overwriting {config_file}")
      ```

* Init_logic.py

  * get_certificate function

    * FailedToRetriveCertificateError - On any case SSL service fails.

      ```python
      try:
          fingerprint, readable_certificate = self.ssl_service.get_certificate(hostname, port)
          logging.debug("Successfully fetched certificate")
      except Exception as error:
          raise Exception(f"Unable to retrieve certificate from {hostname}:{port}. " \
                          f"Reason: {str(error)}") from error
      ```

* login_controller.py

  * get_username function

    * MissingRequiredParameterException - username is missing

      ```python
      self.credential_data.login = input("Enter your login name to log into Conjur: ").strip()
      if self.credential_data.login == '':
          # pylint: disable=raise-missing-from
          raise RuntimeError("Error: Login name is required")
      ```

  * get_api_key function

    * LoginFailedException - Exception thrown on get_api_key from login_logic object

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

  * remove_credentials function

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

    * First exception should raise NotLogedInException
    * Sencod Exception shoud be LogedOutFailed
