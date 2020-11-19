# Contributing

For general contribution and community guidelines, please see the [community repo](https://github.com/cyberark/community).
In particular, before contributing please review our [contributor licensing guide](https://github.com/cyberark/community/blob/master/CONTRIBUTING.md#when-the-repo-does-not-include-the-cla)
to ensure your contribution is compliant with our contributor license agreements.

## Table of Contents

- [Building](#building)
- [Development](#development)
- [Testing](#testing)
- [Pull Request Workflow](#pull-request-workflow)
- [Releasing](#releasing)

Majority of the instructions on how to build, develop, and run the code in
this repo is located in the main [README.md](README.md) but this file adds
any additional information for contributing code to this project.

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

## Testing

### Unit and Integration tests

```
$ ./bin/test
```

### Linting

```
$ ./bin/test_linting
```

### UX Guidelines

See [here](guidelines/python-cli-ux-guidelines.md) for full UX guidelines to follow during development. These guidelines give structure and uniformity when designing and adding CLI commands to the codebase.

## Pull Request Workflow

1. Search the [open issues](../../issues) in GitHub to find out what has been planned
2. Select an existing issue or open an issue to propose changes or fixes
3. Add any relevant labels as you work on it
4. Run tests as described [in the main README](https://github.com/conjurinc/conjur-api-python3#testing),
ensuring they pass
5. Submit a pull request, linking the issue in the description
6. Adjust labels as-needed on the issue. Ask another contributor to review and merge your code if there are delays in merging.

## Releasing

TODO: Define release workflow once we have a PyPI publishing in place
