# conjur-api-python3

Python3-based API SDK for [Conjur OSS v5.x](https://www.conjur.org/) / [AAM Dynamic Access Provider v10.9+](https://www.cyberark.com/products/privileged-account-security-solution/application-access-manager/). The repo also includes a self-contained CLI tool that wraps the API in a simple executable script/binary.

***

### **Status**: Alpha

#### **Warning: Naming and API's are still subject to breaking changes!**

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

#### `set(variable_id, value)`

Sets a variable to a specific value based on its ID.

Note: Policy to create the variable must have been already loaded
otherwise you will get a 404 error during invocation.

## Building

### Egg format

```
$ ./bin/build
```

### Static/portable CLI binary

```
$ ./bin/build_binary
```

## Development

- Create a directory that will hold all the virtualenv packages and files:
```
$ python3 -m venv venv
```

- Enable your terminal to use those files with this command:
```
$ source venv/bin/activate
```

- Install requirements:
```
$ pip3 install -r requirements.txt
```

You can now run the tests and the CLI with modifiable files!

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for additional info on how to contribute
to this repo.

## Testing

### Unit and Integration tests

1. Change the login credentials in `test` file
1. Run `./bin/test`

### Linting

```
$ ./bin/test_linting
```

## License

This project is [licensed under Apache License v2.0](LICENSE.md)
