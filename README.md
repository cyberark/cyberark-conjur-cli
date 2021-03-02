# conjur-api-python3

Command-line tool and programmatic Python access to the Conjur API to manage your Conjur resources. 

This repository includes both the self-contained Conjur command-line tool (`conjur`) and Python3-based SDK for Conjur.

[![Test Coverage](https://api.codeclimate.com/v1/badges/d90d69a3942120b36785/test_coverage)](https://codeclimate.com/github/cyberark/conjur-api-python3/test_coverage) [![Maintainability](https://api.codeclimate.com/v1/badges/d90d69a3942120b36785/maintainability)](https://codeclimate.com/github/cyberark/conjur-api-python3/maintainability)

---

## Certificate level

### CLI

![](https://img.shields.io/badge/Certification%20Level-Certified-6C757D?link=https://github.com/cyberark/community/blob/master/Conjur/conventions/certification-levels.md)

The Conjur CLI is a **Certified** level project. It's been reviewed by CyberArk to verify that it will securely
work with CyberArk DAP as documented. In addition, CyberArk offers Enterprise-level support for these features. For
more detailed information on our certification levels, see [our community guidelines](https://github.com/cyberark/community/blob/master/Conjur/conventions/certification-levels.md#community).

### SDK

![](https://img.shields.io/badge/Certification%20Level-Community-28A745?link=https://github.com/cyberark/community/blob/master/Conjur/conventions/certification-levels.md)

The Conjur Python SDK is a **Community** level project. It's a community contributed project that **is not reviewed or supported
by CyberArk**. For more detailed information on our certification levels, see [our community guidelines](https://github.com/cyberark/community/blob/master/Conjur/conventions/certification-levels.md#community).

### Using conjur-api-python3 with Conjur OSS 

Are you using this project with [Conjur OSS](https://github.com/cyberark/conjur)? Then we 
**strongly** recommend choosing the version of this project to use from the latest [Conjur OSS 
suite release](https://docs.conjur.org/Latest/en/Content/Overview/Conjur-OSS-Suite-Overview.html). 
Conjur maintainers perform additional testing on the suite release versions to ensure 
compatibility. When possible, upgrade your Conjur version to match the 
[latest suite release](https://docs.conjur.org/Latest/en/Content/ReleaseNotes/ConjurOSS-suite-RN.htm); 
when using integrations, choose the latest suite release that matches your Conjur version. For any 
questions, please contact us on [Discourse](https://discuss.cyberarkcommons.org/c/conjur/5).

### Support Services

- Conjur OSS v1.2.0+
- Conjur Enterprise v5.6.3+

### Installation

#### Install the CLI

You can access the latest release of the CLI to install on your machine by navigating to our 
[release](https://github.com/cyberark/conjur-api-python3/releases) page. For instructions on 
how to setup and configure the CLI, see our official documentation ***(TODO add link to docs)*** 

#### Install the SDK

The SDK can be installed via PyPI. Note that the SDK pushed to PyPI does not have the updated
capabilities and experience as the GA CLI version offers. The latest version pushed to PyPI is v.0.1.1.

```
$ pip3 install conjur-client

$ conjur --help
```

Alternatively, you can install the library from the source. Note that this will install the latest work from the
cloned source and not necessarily an official release. Clone the project and run:

```
$ pip3 install .
```

Note: On some machines, you have to use `pip` instead of `pip3` but in most cases,
you will want to use `pip3` if it's available for your platform.

## Usage

### CLI

For more information on how to setup, configure, and start using the CLI, see our official 
documentation found here ***(TODO add link to docs)***.

### SDK

To start using the SDK in your applications, create a Client instance and then invoke the 
API on it:

#### With login ID and password

```python3
#!/usr/bin/env python3

from conjur import Client

client = Client(url='https://conjur.myorg.com',
                account='default',
                login_id='admin',
                password='mypassword',
                ca_bundle='/path/to/my/ca/bundle.pem')

print("Setting variable...")
client.set('conjur/my/variable', 'new value')

print("Fetching variable...")
new_value = client.get('conjur/my/variable')

print("Variable value is:", new_value.decode('utf-8'))
```

#### With login ID and API key

Write the code same as in the first example but initialize the Client with the following arguments:

```python3
client = Client(url='https://conjur.myorg.com',
                account='default',
                login_id='admin',
                api_key='myapikey',
                ca_bundle='/path/to/my/ca/bundle.pem')
```

#### With `.netrc` and `.conjurrc` files

You can provide the above parameters passed in as part of the Client initialization process in two files 
(`.netrc` and `.conjurrc`). Both `.netrc` and `.conjurrc` files should be saved to your home directory. 
For example `~/.netrc`. 

The `.conjurrc` contains connection details needed to connect to the Conjur endpoint and should 
contain details for cert_file, conjur_account, and conjur_url.

```
# .conjurrc
---
cert_file: /Users/someuser/conjur-server.pem
conjur_account: someaccount
conjur_url: https://conjur-server
```

The `.netrc` file or (`_netrc` for Windows environments) contains credentials needed to login the 
Conjur endpoint and should consist of machine, login, and password. Note that the value for 
'machine' should have `/authn` appended to the end of the url and 'password' should contain the 
API key of the user you intend to log in as.

Important! If you choose to create this file yourself, ensure you follow least privilege, allowing only the
user who has created the file to have read/write permissions on it (`chmod 700 .netrc`).

```
# .netrc / _netrc
machine https://conjur-server/authn
login admin
password 1234....
```

Write the code same as in the first example but create the Client 
in the following way:

```
client = Client()
```

## Supported Client methods

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
deleted using the `!delete`, `!revoke`, and `!deny` statements. Unlike
"replace" mode, no data is ever implicitly deleted. Result is a
dictionary object constructed from the returned JSON data.

#### `list()`

Returns a list of all the available resources for the current
account.

#### `whoami()`

_Note: This method requires Conjur v1.9+_

Returns a Python dictionary of information about the client making an
API request (such as its ip address, user, account,
token expiration date etc.).

## Contributing

Instructions for how to deploy a deployment environment and run project tests can be found in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is [licensed under Apache License v2.0](LICENSE.md). Copyright (c) 2021 CyberArk Software Ltd. All rights reserved.
