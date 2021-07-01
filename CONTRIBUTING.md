# Contributing

For general contribution and community guidelines, please see the [community repo](https://github.com/cyberark/community).
In particular, before contributing please review our [contributor licensing guide](https://github.com/cyberark/community/blob/main/CONTRIBUTING.md#when-the-repo-does-not-include-the-cla)
to ensure your contribution is compliant with our contributor license agreements.

## Table of Contents

- [Building](#building)
  * [Static/portable CLI binary](#static-portable-cli-binary)
  * [Egg format](#egg-format)
- [Development](#development)
- [Testing](#testing)
  * [Linting](#linting)
  * [Unit and integration tests](#unit-and-integration-tests)
    + [Running tests in a containerized environment](#running-tests-in-a-containerized-environment)
    + [Running tests outside of a containerized](#running-tests-outside-of-a-containerized)
  * [UX Guidelines](#ux-guidelines)
- [Pull Request Workflow](#pull-request-workflow)
- [Releasing](#releasing)
  * [Checklist](#checklist)
  
Majority of the instructions on how to build, develop, and run the code in
this repo is located in the main [README.md](README.md) but this file adds
any additional information for contributing code to this project.

## Building

### Static/portable CLI binary

```
./bin/build_binary
```
 
NOTE that the executable will be saved to the `dist` directory of the project and can only be run in Ubuntu
 environments.

### Egg format

```
./bin/build
```

## Development

To setup a development environment follow the instructions in this section. Once you have done so, you will
        be able to see live changes made to the CLI.

1. Create a directory that will hold all the `virtualenv` packages and files. Note that you will only need to
        run this command once.

macOS:

```
python3 -m venv venv
```

Windows:

```
py -m venv venv
```

2. Enable your terminal to use those files with this command. Note that this command will need to run each
time you want to return to your virtual environment.

macOS:

```
source venv/bin/activate
```

Windows:

```
venv\Scripts\activate.bat
```

3. Install requirements

```
pip3 install -r requirements.txt
```

4. You can now run the tests and the CLI with modifiable files.

Check it out! Run the following prefix to start seeing changes

```
./pkg_bin/conjur <command> <subcommand>
```

You can also pack the CLI as an executable for OS you are running on. The artifact 
will be saved to the `dist` folder of the project.

```
pyinstaller -F ./pkg_bin/conjur
```

## Testing

### Linting

In the project a linter is used to help enforce coding standards and provides refactoring suggestions.

```
./bin/test_linting
```

### Unit and integration tests

The project's tests can be run in one of two ways:

1. In a containerized environment (Python required)

1. Outside a containerized environment (Python _not_ required)

#### Running tests in a containerized environment

This way of testing allows you to run integration tests in a fail-fast manner. It is recommended to run tests in 
this way during development. When run in a containerized environment, it is possible to run tests as:

1. A full test suite
   
1. An individual test

To run both unit and integration tests as a full test suite run:

```
./bin/test
```

Or to run just the full unit test suite:

```
./bin/test_unit
```

To run specific unit/integration tests, perform the following:

1. Drop into a test container

```
./bin/test_integration -d
```
2. Under the individual test add an identifier of your choosing

```
# Example test function
def my-integration-test()
  ...

my-integration-test.someidentifier=True
```

3. Add the identifier to the following command:

```
# For unit tests
root@123456:/opt/conjur-api-python3# nose2 -v -X --config unit_test.cfg -A '<unit-identifier>'

## Example
root@123456:/opt/conjur-api-python3# nose2 -v -X --config unit_test.cfg -A 'someidentifier'

# For integration tests
root@123456:/opt/conjur-api-python3# nose2 -v -X --config integration_test.cfg -A '<integration-identifier>'

## Example
root@123456:/opt/conjur-api-python3# nose2 -v -X --config integration_test.cfg -A 'someidentifier'
```

4. You should see that only that specific test is run. Every change made locally can be seen in the container. 
   Therefore, you _do not_ need to rebuild before running these tests again.

#### Running tests outside of a containerized

This way of testing allows you to run the integration tests outside a containerized environment and is mainly
  used to test functionality on different platforms before a version release. When run in this way, 
  the integration tests are wrapped in an `integrations_tests_runner` Python module to run in a Python-free environment. 
  Once built, tests can be run as an executable without extra dependencies beyond what the CLI requires to run.

##### Setup

1. Drop in to the development environment and install required dependencies as described in the above [Development](#development) section.

1. Pack the `integrations_tests_runner.py` using PyInstaller in the platform to run the executable.

  To pack: `pyinstaller -F test/util/test_runners/integrations_tests_runner.py`. A new executable will be placed 
  in the `dist`  folder. Note that you will need to pack each runner in each platform that you want to run the tests.

1. Run the created binary `./integrations_tests_runner`, supplying the below required parameters via the command line.

##### Required parameters

`--files-folder` - path to test assets (policy files, etc). This folder is located under `/test` in the
repo. Copy this executable into every OS you wish to run the CLI integration tests.

Parameters like --url, --account, --login, --password values, are used before each test profile is run to configure
  the CLI and run the integration tests successfully.

##### Example

The following is an example of how to run the integration tests. Note paths will differ 
according to the different operating systems so adjustments will be need to be made accordingly.

```
./dist/integrations_tests_runner \
  --url https://conjur-server \
  --account someaccount \
  --login somelogin \
  --password Myp@SS0rdsS1! \
  --files-folder test
```

### UX Guidelines

See [here](guidelines/python-cli-ux-guidelines.md) for full UX guidelines to follow during development. These
  guidelines give structure and uniformity when designing and adding CLI commands to the codebase.

## Pull Request Workflow

1. Search the [open issues](../../issues) in GitHub to find out what has been planned
2. Select an existing issue or open an issue to propose changes or fixes
3. Add any relevant labels as you work on it
4. Run tests as described in the
  [testing section of this document](https://github.com/cyberark/conjur-api-python3/blob/main/CONTRIBUTING.md#testing),
  ensuring they pass
5. Submit a pull request, linking the issue in the description
6. Adjust labels as-needed on the issue. Ask another contributor to review and merge your code if there are delays in
  merging.

## Releasing

The following section provides instructions on what is needed to perform a Conjur CLI release.

### Checklist

1. Run tests in supported platforms
1. Perform security scan
1. Update the version, CHANGELOG, and NOTICES
1. Create Git tag
1. Create release artifacts
1. Sign artifacts
   
1. Add release artifacts to release page

### Run tests in supported platforms

Before each release the following tests will need to be performed:

- On *each* platform we support (macOS, RHEL 7/8, Windows), copy over the compressed archive that holds the CLI executable, 
  decompress it, and [run integration tests](#running-tests-outside-of-a-containerized)
  
- Run the integration tests against the following different Conjur server environments from any platform you choose:
  
  1. An environment configured with a CA-signed certificate (can be configured at the Load Balancer level)
     
  1. An environment configured with a self-signed certificate
     
  1. An environment configured with an unknown CA certificate

  Note environments used to pack the binary should not be the same environment to run the tests!

- Backwards compatibility - deploy Conjur Enterprise v5.6.3 and OSS v1.2.0 servers and
  [run the integration test](#running-tests-outside-of-a-containerized) from each supported platform.
  
### Perform security scan

Scan the project for vulnerabilities.

### Update the version, CHANGELOG, and NOTICES

1. Create a new branch for the version bump.

1. Based on the unreleased content, determine the new version number and update the version in `version.py`.

1. Review the git log and ensure the [CHANGELOG](CHANGELOG.md) contains all relevant recent changes with
  references to GitHub issues or PRs, if possible.

1. Review the changes since the last tag, and if the dependencies have changed revise the [NOTICES](NOTICES.txt)
  file to correctly capture the added dependencies and their licenses / copyrights.

1. Before creating a release, ensure that all documentation that needs to be written has been written by
  TW, approved by PO/Engineer, and pushed to the forward-facing documentation.

1. Commit these changes to the branch. "Bump version to x.y.z" is an acceptable commit message and open a
  PR for review.

### Add a Git tag

1. Once your changes have been reviewed and merged into main, tag the version using `git tag -s v0.1.1`
  for example. Note this requires you to be able to sign releases. Consult
  the [github documentation on signing commits](https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/managing-commit-signature-verification)
  on how to set this up. 

  "vx.y.z" is an acceptable tag message

1. Push the tag: `git push vx.y.z` (or `git push origin vx.y.z` if you are working from your local machine).

### Create release artifacts

Currently, packing the client into an executable is a manual process. For Linux and Windows, you will need to
  pack the client using the different VMs we have available to us. For macOS, you will need to use your local machine.
See the below section _How to create release artifacts_ for detailed information on how to create CLI binaries.

*Important!* The final artifacts that are delivered to the customer should be created from the main branch

### Sign artifacts

- Sign Windows executable

- Sign RHEL 7/8 executable

- Sign and notarize the ConjurCLI app for macOS 

*Important!* The final artifacts that are delivered to the customer should be created from the main branch

### How to create release artifacts

For all OS types perform the following:
1. Clone the repo by running `git clone https://github.com/cyberark/conjur-api-python3.git`.
1. Activate the development and install the requirements as described in the above [Development](#development) section.
1. Run `pip3 install -r requirements.txt` to install all the project's dependencies.

#### RHEL 7/8

1. Run `pyinstaller -F ./pkg_bin/conjur` on the different RHEL 7 and RHEL 8 machines. Once this is run, a `dist` folder 
   will be created with the executable in it.
1. Once an executable has been created, archive the file for RHEL 7 and RHEL 8 platforms, using the following commands:
  1. `tar cvf conjur-cli-rhel-7.tar.gz conjur`
  1. `tar cvf conjur-cli-rhel-8.tar.gz conjur`
1. Sign the archive and add the following files as assets in the release page.
  1. The archive (i.e `*.tar.gz`)
  1. The signature file (i.e `*.tar.gz.sig`)
  1. The public key (`RPM-GPG-KEY-CyberArk`)

#### macOS

1. Run `pyinstaller -D ./pkg_bin/conjur`. Once this is run, a `dist` folder will be created with the executable in it.
1. Follow the instructions on how to build the DMG and how to sign and notarize the CLI.
1. Add the conjurcli.dmg as an asset in the release page.

NOTE that the macOS executable is packed as a directory instead of a file for performance purposes.

#### Windows

1. Run `pyinstaller -F ./pkg_bin/conjur`. Once this is run, a `dist` folder will be created with the executable
  in it.
1. Once an executable has been created, zip the executable (`zip conjur-cli-windows.zip conjur`).
1. Sign the `zip` and add it as an asset in the release page.

To copy files over from Windows VM to your local machine, use Remote Desktop redirection. In the Remote Desktop app,
  perform the following:

1. Edit the machine and navigate to *Folders*.
1. Click on *Redirect folders* and enter the path of the shared folder. Note that you will need to establish a new
  connection to see the changes.
1. Drag the executable/zip to the shared folder. You should now see it on your local machine.

The archives should be called the following:

```
conjur-cli-rhel-7.tar.gz
conjur-cli-rhel-8.tar.gz
conjur-cli-windows.zip
conjurcli.dmg
```
