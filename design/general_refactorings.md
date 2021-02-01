## CLI Refactor

------

The purpose of this document is to outline the parts of the Python CLI/SDK code that we would like to refactor as well as provide a design for each point. Through this refactor, we hope that the code will be more readable, and easier to contribute to and maintain.



### Improve Naming

------

Improve Naming. Go over names of files, functions, folder, classes and rename to more readable names.

For example `class Resource` should be `class ConjurResource` so code reader would understand it is a conjur resource. Same about the name of that file.+

### Organize directory structure

------

##### Proposal

Create new stracture of directories divided by the type of the file and their responsibily. For example all control classes in one directory

##### Current State

Currently directories resemble the following structure:

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

And the following files are without parent directories and sit in the main directory. : api.py, client.py, argparse_wrapper.py, cli.py , client.py, config.py, constants.py, credentials_data.py, credentials_form_file.py, endpoint.py, errors.py, http_wrapper.py, resource.py, ssl_service.py, version.py

##### Recommendation

The change i want to make is to organize the files by their types and not by the command they do and have directories that can be used for the files without directory:

| Directory Name | Purpose                                                      |
| :------------- | :----------------------------------------------------------- |
| utils          | wrappers and utils of diffrent python libsssl_servicearg_parse_wrapperhttp_wrapper |
| api            | files that talk directly with conjur.  conjur_client.py (conjur.py) , conjur_api.py (api.py), ssl_client.py (ssl_service) |
| logics         | all logic classes here                                       |
| controllers    | all controller classes                                       |
| logics         | all logic classes                                            |
| data_objects   | all data objects classes                                     |



### Improve Error Handling

------

##### Proposal

Raise only our own exceptions and not built in or libs exceptions. Helps to better understand the error handling flow
and allows us to catch our own objects and not general exceptions.  In addition all exception should be documented.

##### Current state

Through the codebase, we have very general errors that are not representative of the actual error that took place. The exception is not documented
For example in `get_certificate` function we do :

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

Go over error and exception handling and create Conjur-specific exceptions. The code block above should be:

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
            raise CertificateRetrivialFailed(f"Unable to retrieve certificate from {hostname}:{port}. " \
                            f"Reason: {str(error)}") from error

        return fingerprint, readable_certificate
```

The document improve_error_handling_to_do_list goes over all error handling block where change of the raised object need to be done.

------

### Strong-type function parameters and return types

##### Proposal

Strong-type all parameters and function return types as per Python3 best practices

##### Current state

Functions are not strongly typed. For example this function:

`def get_variable(self, variable_data):`

##### Recommendation

Strongly Type the function so it will be like this.

`def get_variable(self, variable_data : VariableData) -> str:`

------

### Explicit Import Statements

##### Proposal

Make sure all import statement in the code in explicit and involve full path. Its the correct way to import in python and helps readr to see which model we mean if the are more then one class we same name.

##### Current state

There are implicit import statement in the code

```python
from .client import Client
```

##### Recommendation

Use explicit imnport statements

```python
from conjur.client import Client
```