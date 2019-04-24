# conjur-api-python3

Python3-based API SDK for [Conjur OSS](https://www.conjur.org/). The repo
also includes a self-contained CLI tool that wraps the API in a simple executable
script/binary.

***

### **Status**: Alpha

#### **Warning: Naming and APIs are still subject to breaking changes!**

***


## Installing the code

### From PyPI

TODO: Publish the package on PyPI

### From source

```
$ pip3 install .
```

Note: On some machines, you have to use `pip` instead of `pip3` but in most cases,
you will want to use `pip3` if it's available for your platform.

## Usage

Most usage is done by creating a Client instance and then invoking the API on it:

```python3
#!/usr/bin/env python3

from conjur_api_python3 import Client

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

### Currently supported client methods:

#### `get(variable_id)`

Gets a variable value based on its ID. Variable is binary data
that should be decoded to your system's encoding (e.g.
`get(variable_id).decode('utf-8')`.

#### `get_many(variable_id[,variable_id...])`

Gets multiple variable values based on their IDs. Variables are
returned in a python dictionary that maps the variable name to its
value.

#### `set(variable_id, value)`

Sets a variable to a specific value based on its ID.

Note: Policy to create the variable must have been already loaded
otherwise you will get a 404 error during invocation.

#### `apply_policy_file(policy_name, policy_file)`

Applies a file-based YAML to a named policy. This method only
supports additive changes.

#### `replace_policy_file(policy_name, policy_file)`

Replaces a named policy with one from the provided file. This is
usually a destructive invocation.


## Contributing

We store instructions for development and guidelines for how to build and test this
project in the [CONTRIBUTING.md](CONTRIBUTING.md) - please refer to that document
if you would like to contribute.

## License

This project is [licensed under Apache License v2.0](LICENSE.md)
