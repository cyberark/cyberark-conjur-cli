# conjur-api-python3

Python3-based API SDK for [Conjur OSS](https://www.conjur.org/). The repo also includes a self-contained CLI tool (`conjur`) that wraps the API in a simple executable script/binary.

[![Test Coverage](https://api.codeclimate.com/v1/badges/d90d69a3942120b36785/test_coverage)](https://codeclimate.com/github/cyberark/conjur-api-python3/test_coverage) [![Maintainability](https://api.codeclimate.com/v1/badges/d90d69a3942120b36785/maintainability)](https://codeclimate.com/github/cyberark/conjur-api-python3/maintainability)

---

### **Status**: Alpha

#### **Warning: Naming and APIs are still subject to breaking changes!**

---

## Installing the code

### Using conjur-api-python3 with Conjur OSS 

Are you using this project with [Conjur OSS](https://github.com/cyberark/conjur)? Then we **strongly** recommend choosing the version of this project to use from the latest [Conjur OSS suite release](https://docs.conjur.org/Latest/en/Content/Overview/Conjur-OSS-Suite-Overview.html). 
Conjur maintainers perform additional testing on the suite release versions to ensure 
compatibility. When possible, upgrade your Conjur version to match the 
[latest suite release](https://docs.conjur.org/Latest/en/Content/ReleaseNotes/ConjurOSS-suite-RN.htm); when using integrations, choose the latest suite release that matches your Conjur version. For any questions, please contact us on [Discourse](https://discuss.cyberarkcommons.org/c/conjur/5).

### About our releases

#### Github releases

GitHub releases are created for GitHub tagged versions that have undergone additional quality testing. For all release versions 7+, we push the new release archive files for each of our supported platforms to [our release page](https://github.com/cyberark/conjur-api-python3/releases).

Once installed from the release page, you can extract the archieve by running `tar -xf conjur-cli-<platform>.tar.gz`

We recommend that you move the `conjur` executable to your `/usr/local/bin` path so that the CLI will be available from anywhere on your machine.

#### From PyPI

With every release, we push the updated client to PyPI. You can install our client via PyPI by running:

```
$ pip3 install conjur-client
```

#### GitHub repository

The code on `master` in the project's GitHub repository represents the development work done since the previous GitHub tag. It is possible to build the project from source by running:

```
$ pip3 install .
```

Note: On some machines, you have to use `pip` instead of `pip3` but in most cases,
you will want to use `pip3` if it's available for your platform.

For regular use, we recommend taking the archive files from [our release page](https://github.com/cyberark/conjur-api-python3/releases).

### Update from Ruby to Python CLI

To ensure a smooth experience moving from the Ruby to Python CLI, we recommend that you either remove the Ruby CLI from your machine or rename it.

To do so:

1. Run `which conjur` to get the path of the Ruby CLI gem
2. Navigate to the outputted path and either remove it or update it `conjur.v6`

## Commands

| Command | Description                                              |
| ------- | -------------------------------------------------------- |
| authn   | - Log in and log out                                     |
| list    | - List all available resources belonging to this account |
| policy  | - Manage policies                                        |
| whoami  | - Provide information about the current logged-in user   |

## Usage

### CLI

CLI can either be used with the included executable script:

```shell
conjur-cli --insecure -l https://myserver -a orgname -u admin -p secret \
  variable get foo/bar
```

Or through the installed module:

```shell
python -m conjur --insecure -l https://myserver -a orgname -u admin -p secret list
```

### API

Most usage is done by creating a Client instance and then invoking the API on it:

#### With login ID and password

```python3
#!/usr/bin/env python3

from conjur import Client

client = Client(url='https://conjur.myorg.com',
                account='default',
                login_id='admin',
                password='mypassword',
                ca_bundle='/path/to/my/ca/bundle')

print("Setting variable...")
client.set('conjur/my/variable', 'new value')

print("Fetching variable...")
new_value = client.get('conjur/my/variable')

print("Variable value is:", new_value.decode('utf-8'))
```

#### With login Id and API key

Write the code same as in the first example but create the client with the following arguments:

```python3
client = Client(url='https://conjur.myorg.com',
                account='default',
                login_id='admin',
                api_key='myapikey',
                ca_bundle='/path/to/my/ca/bundle')
```

#### With `.netrc` and `.conjurrc` settings

Write the code same as in the first example but create the client with the following arguments:

```python3
client = Client()
```

## Currently supported client methods:

#### `get(variable_id)`

Gets a variable value based on its ID. Variable is binary data
that should be decoded to your system's encoding (e.g.
`get(variable_id).decode('utf-8')`.

#### `get_many(variable_id[,variable_id...])`

Gets multiple variable values based on their IDs. Variables are
returned in a dictionary that maps the variable name to its value.

#### `set(variable_id, value)`

Sets a variable to a specific value based on its ID.

Note: Policy to create the variable must have been already loaded
otherwise you will get a 404 error during invocation.

#### `apply_policy_file(policy_name, policy_file)`

Applies a file-based YAML to a named policy. This method only
supports additive changes. Result is a dictionary object constructed
from the returned JSON data.

#### `replace_policy_file(policy_name, policy_file)`

Replaces a named policy with one from the provided file. This is
usually a destructive invocation. Result is a dictionary object
constructed from the returned JSON data.

#### `delete_policy_file(policy_name, policy_file)`

Modifies an existing Conjur policy. Data may be explicitly
deleted using the !delete, !revoke, and !deny statements. Unlike
"replace" mode, no data is ever implicitly deleted. Result is a
dictionary object constructed from the returned JSON data.

#### `list()`

Returns a Python list of all the available resources for the current
account.

#### `whoami()`

_Note: This method requires Conjur v1.9+_

Returns a Python dictionary of information about the client making an
API request (such as its ip address, user, account,
token expiration date etc.).



## Contributing

We store instructions for development and guidelines for how to build and test this
project in the [CONTRIBUTING.md](CONTRIBUTING.md) - please refer to that document
if you would like to contribute.

## License

This project is [licensed under Apache License v2.0](LICENSE.md)
