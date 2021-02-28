# Contributing

For general contribution and community guidelines, please see the [community repo](https://github.com/cyberark/community).
In particular, before contributing please review our [contributor licensing guide](https://github.com/cyberark/community/blob/master/CONTRIBUTING.md#when-the-repo-does-not-include-the-cla)
to ensure your contribution is compliant with our contributor license agreements.

## Table of Contents

- [Building](#building)
  * [Static/portable CLI binary](#static-portable-cli-binary)
  * [Egg format](#egg-format)
- [Development](#development)
- [Testing](#testing)
  * [Linting](#linting)
  * [Unit and Integration tests](#unit-and-integration-tests)
    + [Running in a containerized environment](#running-in-a-containerized-environment)
    + [Running tests on different platforms](#running-tests-on-different-platforms)
  * [UX Guidelines](#ux-guidelines)
- [Pull Request Workflow](#pull-request-workflow)
- [Releasing](#releasing)
  * [Run tests](#run-tests)
  * [Update the version, changelog, and notices](#update-the-version--changelog--and-notices)
  * [Add a git tag](#add-a-git-tag)
  * [Create release artifacts](#create-release-artifacts)

Majority of the instructions on how to build, develop, and run the code in
this repo is located in the main [README.md](README.md) but this file adds
any additional information for contributing code to this project.

## Building

### Static/portable CLI binary

```
$ ./bin/build_binary
```

### Egg format

```
$ ./bin/build
```

## Development

To setup a development environment follow the instructions in this section. Once you have done so, you will
        be able to see live changes made to the CLI.

1. Create a directory that will hold all the `virtualenv` packages and files. Note that you will only need to
        run this command once.

macOS:

```
$ python3 -m venv venv
```

Windows:

```
$ py -m venv venv
```

1. Enable your terminal to use those files with this command. Note that this command will need to run each
time you want to return to your virtual environment.

macOS:

```
$ source venv/bin/activate
```

Windows:

```
$ venv\Scripts\activate.bat
```

1. Install requirements

```
$ pip3 install -r requirements.txt
```

1. You can now run the tests and the CLI with modifiable files.

Check it out! Run the following prefix to start seeing changes

```
$ ./pkg_bin/conjur <command> <subcommand>
```

## Testing

### Linting

In the project a linter is used to help enforce coding standards and provides refactoring suggestions.

```
$ ./bin/test_linting
```

### Unit and Integration tests

To run both unit and integration tests at once in a containerized environment:

```
$ ./bin/test
```

To run unit tests:
```
./bin/test_unit
```

You can run integration tests in the following ways:
1. Running tests from a containerized environment

1. Running tests on different platforms

#### Running in a containerized environment

This way of testing allows you to run integration tests in a fail-fast manner. It is recommended to run
  tests in this way during development.

To run specific tests, perform the following:

1. Drop down into a test container

```
$ ./bin/test_integration -d
```

1. Under the individual test add an identifier of your choosing

For example:

```
# Example test function
def my-integration-test()
  ...

my-integration-test.someidentifier=True
```

1. Add the identifier to the following command:

```
root@123456:/opt/conjur-api-python3# nose2 -v -X --config integration_test.cfg -A '<identifier>' $@

## Example
root@123456:/opt/conjur-api-python3# nose2 -v -X --config integration_test.cfg -A 'someidentifier' $@
```

1. You should see that only that specific test is run. Every change made locally can be seen in the container so you
do *not* need to rebuild before running these tests again.

#### Running tests on different platforms

This way of testing allows you to run the integration tests outside a containerized environment and is mainly
  used to test functionality of different platforms before a version release.

We provide the option to run the integration tests as a regular integration test or as a separate process.
  Running as a process means integration tests can run in the same way a user would use our CLI- without Python
  installed on the machine, using the same Conjur CLI executable given to end users.

Regardless of the way the integrations are run for this use-case, they are wrapped in an integration_test_runner
  Python module to run in a Python-free environment. That way tests can be run cross-platform.

##### Setup

1. Pack the `integration_test_runner.py` using PyInstaller in the platform to run the executable.

  To pack: `pyinstaller -F test/util/test_runners/integration_test_runner.py`. Note that you will need
  to pack each runner in each platform that you want to run the tests.

1. Pack the Conjur CLI using PyInstaller in the platform to run the executable

  To pack: `pyinstaller -F ./pkg_bin/conjur`. Note that you will need to pack each runner in each platform
  that you want to run the tests. Also note that _only_ for macOS, you should pack the CLI as a directory instead of a
  single file (using -D instead of -F). This will allow the CLI tests to run quicker.

1. Run the executable: `./integration_test_runner`, supplying the below required parameters via the command line.

##### Required parameters

`--invoke-cli-as-process` - required only to run the CLI as a process. If required to run as a regular integration
  test, this is not required.

`--cli-to-test` - path to the packed CLI executable to test against.

Parameters like --url, --account, --login, --password values, are used before each test profile is run to configure
  the CLI and run the integration tests successfully.

`--identifier` - the test method with this identifier will be run (`integration` by default).
To run as a process, the identifier should be `test_with_process`.

`--files-folder` - path to test assets (policy files, etc). This folder is located under `/test` in the
repo. Copy this executable into every OS you wish to run the CLI integration tests.

##### Example

Note paths will differ according to the different operating systems so adjustments will be need to be made accordingly.

```
./integrations_tests_runner \
  --identifier test-with-process \
  --url https://conjur-server \
  --account someaccount \
  --login somelogin \
  --password Myp@SS0rds1! \
  --files-folder /test \
  --cli-to-test /conjur \
  --invoke-cli-as-process
```

### UX Guidelines

See [here](guidelines/python-cli-ux-guidelines.md) for full UX guidelines to follow during development. These
  guidelines give structure and uniformity when designing and adding CLI commands to the codebase.

## Pull Request Workflow

1. Search the [open issues](../../issues) in GitHub to find out what has been planned
2. Select an existing issue or open an issue to propose changes or fixes
3. Add any relevant labels as you work on it
4. Run tests as described in the
  [testing section of this document](https://github.com/cyberark/conjur-api-python3/blob/master/CONTRIBUTING.md#testing),
  ensuring they pass
5. Submit a pull request, linking the issue in the description
6. Adjust labels as-needed on the issue. Ask another contributor to review and merge your code if there are delays in
  merging.

## Releasing

The following section provides instructions on what is needed to perform a Conjur CLI release.

### Checklist

1. Run tests
1. Perform security scan
1. Update the version, changelog, and notices
1. Add a git tag
1. Add release artifacts

### Run tests

 Before each release the following will need to be performed:

- On *each* platform we support (macOS, RHEL 7/8, Windows), pass the archived file, decompress, and
  [run integration tests](#running-tests-on-different-platforms) against three different types of environments:

  1. An environment configured with a CA-signed certificate
  1. An environment configured with a self-signed certificate
  1. An environment configured with an unknown CA certificate

  Note environments used to compress the archive should not be the same environment to run the tests!

- Backwards compatibility - deploy DAP v5.6.3 and OSS v1.2.0 servers and
  [run the integration test](running-tests-on-different-platforms) from each supported platform.

- Run tests as process in environments that support this - MacOS and RHEL 7 / 8. Note that currently we
  cannot run our integration tests as a process in Windows platforms.

- Sanity checks - on *each* platform run `init`, `login`, `list`, ensuring you are able to get end to end.

### Perform security scan

Scan the project for vulnerabilities

### Update the version, changelog, and notices

1. Create a new branch for the version bump

1. Based on the unreleased content, determine the new version number and update the version in `version.py`

1. Review the git log and ensure the [CHANGELOG](CHANGELOG.md) contains all relevant recent changes with
  references to GitHub issues or PRs, if possible

1. Review the changes since the last tag, and if the dependencies have changed revise the [NOTICES](NOTICES.txt)
  file to correctly capture the added dependencies and their licenses / copyrights

1. Before creating a release, ensure that all documentation that needs to be written has been written by
  TW, approved by PO/Engineer, and pushed to the forward-facing documentation

1. Commit these changes to the branch. "Bump version to x.y.z" is an acceptable commit message and open a
  PR for review

### Add a git tag

1. Once your changes have been reviewed and merged into master, tag the version using `git tag -s v0.1.1`
  for example. Note this requires you to be able to sign releases. Consult
  the [github documentation on signing commits](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/managing-commit-signature-verification)
  on how to set this up. 

  "vx.y.z" is an acceptable tag message

1. Push the tag: `git push vx.y.z` (or `git push origin vx.y.z` if you are working from your local machine)

### Create release artifacts

Currently, packing the client into an executable is a manual process. For Linux and Windows, you will need to
  pack the client using the different VMs we have available to us. For macOS, you will need to use your local machine.

#### For all OS types:

1. Clone the repo by running `git clone https://github.com/cyberark/conjur-api-python3.git`
1. Install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) and
  [Python](https://realpython.com/installing-python/) if not already on the machine
1. Activate [venv](#development) and install the requirements

#### Linux

1. Run `./bin/build_binary --local`. Once this is run, a `dist` folder will be created with the executable in it
1. Once an executable has been created, run `tar -cvf conjur-cli-linux.tar.gz conjur` to archive the file in a
  `tar.gz` format
1. Sign the `tar.gz` and add the archive file as an asset in the release

#### macOS

1. Run `./bin/build_binary --local`. Once this is run, a `dist` folder will be created with the executable in it
1. Once an executable has been created, run `tar -cvf conjur-cli-darwin.tar.gz conjur` to archive the file in a
  `tar.gz` format
1. Sign the `tar.gz` and add the archive file as an asset in the release

#### Windows

1. Run `pyinstaller --onefile pkg_bin/conjur`. Once this is run, a `dist` folder will be created with the executable
  in it
1. Once an executable has been created, zip the executable (`zip conjur-cli-windows.zip conjur`)
1. Sign the `.zip` and add the zip as an asset in the release

To copy files over from Windows VM to your local machine, use Remote Desktop redirection. In the Remote Desktop app,
  perform the following:

1. Edit the machine and navigate to *Folders*
1. Click on *Redirect folders* and enter the path of the shared folder. Note that you will need to establish a new
  connection to see the changes
1. Drag the executable/zip to the shared folder. You should now see it on your local machine

The archive files should be called the following:

```
conjur-cli-linux.tar.gz
conjur-cli-darwin.tar.gz
conjur-cli-windows.zip
```
