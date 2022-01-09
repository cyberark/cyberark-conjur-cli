# conjur-api-python3

This repository includes both the self-contained Conjur command-line tool (`conjur`) and the
Python3-based SDK for accessing the Conjur API to manage Conjur resources.

[![Test Coverage](https://api.codeclimate.com/v1/badges/d90d69a3942120b36785/test_coverage)](https://codeclimate.com/github/cyberark/conjur-api-python3/test_coverage) [![Maintainability](https://api.codeclimate.com/v1/badges/d90d69a3942120b36785/maintainability)](https://codeclimate.com/github/cyberark/conjur-api-python3/maintainability)

---

## Certificate level

### Conjur CLI

![](https://img.shields.io/badge/Certification%20Level-Certified-6C757D?link=https://github.com/cyberark/community/blob/main/Conjur/conventions/certification-levels.md)

The Conjur CLI is a **Certified** level project. It's been reviewed by CyberArk to verify that it
will securely work with CyberArk Conjur Enterprise (previously known as DAP) as documented. In
addition, CyberArk offers Enterprise-level support for these features. For more detailed information
on our certification levels,
see [our community guidelines](https://github.com/cyberark/community/blob/main/Conjur/conventions/certification-levels.md#community)
.

### Conjur Python SDK

![](https://img.shields.io/badge/Certification%20Level-Community-28A745?link=https://github.com/cyberark/community/blob/main/Conjur/conventions/certification-levels.md)

The Conjur Python SDK is a **Community** level project. It's a community contributed project that **
is not reviewed or supported by CyberArk**. For more detailed information on our certification
levels,
see [our community guidelines](https://github.com/cyberark/community/blob/main/Conjur/conventions/certification-levels.md#community)
.

### Using conjur-api-python3 with Conjur Open Source

Are you using this project with [Conjur Open Source](https://github.com/cyberark/conjur)? Then we
**strongly** recommend choosing the version of this project to use from the
latest [Conjur OSS suite release](https://docs.conjur.org/Latest/en/Content/Overview/Conjur-OSS-Suite-Overview.html)
. Conjur maintainers perform additional testing on the suite release versions to ensure
compatibility. When possible, upgrade your Conjur Open Source version to match the
[latest suite release](https://docs.conjur.org/Latest/en/Content/ReleaseNotes/ConjurOSS-suite-RN.htm)
. When using integrations, choose the latest suite release that matches your Conjur Open Source
version. For any questions, please contact us
on [Discourse](https://discuss.cyberarkcommons.org/c/conjur/5).

### Supported Services

- Conjur Open Source v1.2.0 or later
- Conjur Enterprise v11.2.1 (v5.6.3) or later

### Sypported Platforms

- macOS Catalina or later
- Windows 10 or later
- Red Hat Enterprise Linux 7, 8

### Installation

#### Install the Conjur CLI

To access the latest release of the Conjur CLI, go to
our [release](https://github.com/cyberark/conjur-api-python3/releases)
page. For instructions on how to set up and configure the CLI, see
our [official documentation](https://docs.conjur.org/Latest/en/Content/Developer/CLI/cli-lp.htm).

#### Install the SDK

The SDK can be installed via PyPI. Note that the SDK is a **Community** level project meaning that
the SDK is subject to alterations that may result in breaking change.

To avoid unanticipated breaking changes, make sure that you stay up-to-date on our latest releases
and review the project's [CHANGELOG.md](CHANGELOG.md).

```
pip3 install conjur

conjur --help
```

Alternatively, you can install the library from the source. Note that this will install the latest
work from the cloned source and not necessarily an official release.

Clone the project and run:

```
pip3 install 
```

## Usage

### CLI

For more information on how to set up, configure, and start using the Conjur CLI, see
our [official documentation](https://docs.conjur.org/Latest/en/Content/Developer/CLI/cli-lp.htm).

### SDK

To start using the SDK in your applications, create a Client instance and then invoke the API on it:

#### With login ID and password

```python3
#!/usr/bin/env python3

from conjur import Client

client = Client(conjurrc_data=ConjurrcData(...),
                ssl_verification_mode=SslVerificationMode.TRUST_STORE,
                credentials_provider=FileCredentialsProvider(),
                debug=False)

print("Setting variable...")
client.set('conjur/my/variable', 'new value')

print("Fetching variable...")
new_value = client.get('conjur/my/variable')

print("Variable value is:", new_value.decode('utf-8'))
```

#### Defining the Conjur server endpoint

A configuration file called `.conjurrc` is used to hold details required to communicate to the
Conjur server. You can provide these details needed to open a connection to the Conjur endpoint in
this file instead of passing them in (`url`, `account`, and `ca_bundle`)  
during initialization of the Client.

The `.conjurrc` file should be saved to your home directory and should contain `conjur_url`,
`conjur_account`, and`cert_file`.

```
# .conjurrc
---
cert_file: /Users/someuser/conjur-server.pem
conjur_account: someaccount
conjur_url: https://conjur-server
```

#### Storing credentials

When using the SDK, you can keep credentials in the system's native credential store instead of
passing them in during initialization of the Client. By default, the Client will favor saving
credentials (login ID and password) to the system's credential store. If the detected credential
store is not one we support or is not accessible, the credentials will be written to a configuration
file, `.netrc`, in plaintext.

If written to the `.netrc`, it is strongly recommended that you log out when not using the Conjur
CLI. This removes the credentials from the `.netrc` file.

The `.netrc` file or (`_netrc` for Windows environments) contains credentials needed to log in to
the Conjur endpoint and should consist of 'machine', 'login', and 'password'.

Note that if you choose to create this file yourself, ensure you follow least privilege, allowing
only the user who has created the file to have read/write permissions on it (`chmod 700 .netrc`).

```
# .netrc / _netrc
machine https://conjur.myorg.com
login admin
password 1234....
```

## Supported Client methods

#### `get(variable_id)`

Gets a variable value based on its ID. Variable is binary data that should be decoded to your system's encoding (e.g.
`get(variable_id).decode('utf-8')`.

#### `get_many(variable_id[,variable_id...])`

Gets multiple variable values based on their IDs. Variables are returned in a dictionary that maps the variable name to
its value.

#### `set(variable_id, value)`

Sets a variable to a specific value based on its ID.

Note: Policy to create the variable must have already been loaded otherwise you will get a 404 error during invocation.

#### `load_policy_file(policy_name, policy_file)`

Applies a file-based YAML to a named policy. This method only supports additive changes. Result is a dictionary object
constructed from the returned JSON data.

#### `replace_policy_file(policy_name, policy_file)`

Replaces a named policy with one from the provided file. This is usually a destructive invocation. Result is a
dictionary object constructed from the returned JSON data.

#### `update_policy_file(policy_name, policy_file)`

Modifies an existing Conjur policy. Data may be explicitly deleted using the `!delete`, `!revoke`, and `!deny`
statements. Unlike
"replace" mode, no data is ever implicitly deleted. Result is a dictionary object constructed from the returned JSON
data.

#### `list(list_constraints)`

Returns a list of all available resources for the current account.

The 'list constraints' parameter is optional and should be provided as a dictionary.

For example: `client.list({'kind': 'user', 'inspect': True})`

| List constraints | Explanation                                                  |
| ---------------- | ------------------------------------------------------------ |
| kind             | Filter resources by specified kind (user, host, layer, group, policy, variable, or webservice) |
| limit            | Limit list of resources to specified number                  |
| offset           | Skip specified number of resources                           |
| role             | Retrieve list of resources that specified role is entitled to see (must specify role's full ID) |
| search           | Search for resources based on specified query                |
| inspect          | List the metadata for resources                              |

#### `def list_permitted_roles(list_permitted_roles_data: ListPermittedRolesData)`

Lists the roles which have the named permission on a resource.

#### `def list_members_of_role(data: ListMembersOfData)`

Lists the resources which are members of the given resource.

#### `def create_token(create_token_data: CreateTokenData)`

Create hostfactory token/s for creating hosts

#### `def create_host(create_host_data: CreateHostData)`

Use hostfactory token to create host

#### `def revoke_token(token: str)`

Revokes the given token

#### `rotate_other_api_key(resource: Resource)`

Rotates another entity's API key and returns it as a string.

Note: resource is of type Resource which should have `type` (user / host) and
`name` attributes.

#### `rotate_personal_api_key(logged_in_user, current_password)`

Rotates the personal API key of the logged-in user and returns it as a string.

#### `change_personal_password(logged_in_user, current_password, new_password)`

Updates the current, logged-in user's password with the password parameter provided.

Note: the new password must meet the Conjur password complexity constraints. It must contain at least 12 characters: 2
uppercase, 2 lowercase, 1 digit, 1 special character.

#### `whoami()`

_Note: This method requires Conjur v1.9+_

Returns a Python dictionary of information about the Client making an API request (such as its IP address, user,
account, token expiration date, etc).

## Contributing

Instructions for how to deploy a deployment environment and run project tests can be found
in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is [licensed under Apache License v2.0](LICENSE.md). Copyright (c) 2021 CyberArk
Software Ltd. All rights reserved.
