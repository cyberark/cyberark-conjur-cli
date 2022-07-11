# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased

## [7.2.0] - 2022-07-11

### Changed
- Revert conjurrc key names to match Ruby CLI.
  [cyberark/cyberark-conjur-cli#413](https://github.com/cyberark/cyberark-conjur-cli/pull/413)

### Added
- Support authn-ldap
  [cyberark/cyberark-conjur-cli#411](https://github.com/cyberark/cyberark-conjur-cli/pull/411)

### Fixed
- Corrected the `tar` command in the RHEL release steps.
  [cyberark/cyberark-conjur-cli#406](https://github.com/cyberark/cyberark-conjur-cli/pull/406)

### Removed
- `SDK` with all it contents was removed and is now maintained in the https://github.com/cyberark/conjur-api-python repository

## [7.1.0] - 2021-12-22

### Added
- `Init` command is now strict to run in one of three modes described in `SslVerificationMode` enum
- For CLI `Init` flow, Additional certificate validation steps where added. for --self-signed and --ca-cert flows
- Support http domains if working in insecure mode
- The `hostfactory` method `create token` is now available in CLI and SDK to create a hostfactory token to manage hosts
  and permissions in a dynamic way
  [cyberark/cyberark-conjur-cli#339](https://github.com/cyberark/cyberark-conjur-cli/pull/339)
- Stop supporting `Client` initialization from disk.
- The list options `--members-of`, `--permitted-roles`, and `--privilege` are now available in the Conjur CLI

### Fixed
- Fixed Load policy "hides" the error message

## [7.0.1] - 2020-04-12

### Added
- The CLI has promoted to GA. The SDK still remains a community level project.
- The `host` method 'rotate-api-key' is now available in CLI and SDK to manage hosts
  [cyberark/cyberark-conjur-cli#101](https://github.com/cyberark/cyberark-conjur-cli/issues/101)
- The `user` methods 'rotate-api-key' and 'change-password' are now available in CLI and SDK to manage users
  [cyberark/cyberark-conjur-cli#101](https://github.com/cyberark/cyberark-conjur-cli/issues/101)
- Previous versions of a variable/secret can now be retrieved. This is available in both CLI and SDK
  [cyberark/cyberark-conjur-cli#151](https://github.com/cyberark/cyberark-conjur-cli/issues/151)
- The `list` flag constraints are now available in both CLI and SDK to filter resource results
  [cyberark/cyberark-conjur-cli#128](https://github.com/cyberark/cyberark-conjur-cli/issues/91)
- The `login\logout` methods are now available in CLI to login and out of the CLI
  [cyberark/cyberark-conjur-cli#128](https://github.com/cyberark/cyberark-conjur-cli/issues/128)
- The `init` method is now available in CLI to initialize the CLI with the Conjur server
  [cyberark/cyberark-conjur-cli#89](https://github.com/cyberark/cyberark-conjur-cli/issues/89)

### Changed
- The CLI and SDK now use a system's native credential store to save credentials instead of a netrc file by default. If
  a store is not available, the credentials will be saved to the netrc as a fallback. [cyberark/cyberark-conjur-cli#NO]()
- The CLI/SDK package pushed to Pypi has changed from `conjur-client` to `conjur`. [cyberark/cyberark-conjur-cli#NO]()
- The .conjurrc parameters have been renamed from `account` to `conjur_account` and from `appliance_url` to `conjur_url`
  . Additionally, the plugins parameter has been removed. This is a breaking change for users who generate their own
  .conjurrc file for use in the SDK and will need to update accordingly.
  [cyberark/cyberark-conjur-cli#206](https://github.com/cyberark/cyberark-conjur-cli/issues/206)
- Policy functions `apply_policy_file` and `delete_policy_file` have been replaced with `load_policy_file` and
  `update_policy_file` respectively. This is a breaking change and users who import the SDK will need to update these
  references in their
  projects [cyberark/cyberark-conjur-cli#112](https://github.com/cyberark/cyberark-conjur-cli/issues/112)
- CLI command UX has been improved according to UX guidelines
  [cyberark/cyberark-conjur-cli#132](https://github.com/cyberark/cyberark-conjur-cli/issues/132)
  See [design guidelines](https://ljfz3b.axshare.com/#id=x8ktq8&p=conjur_help__init&g=1)
- Update help screens according to [these guidelines](https://ljfz3b.axshare.com/#id=yokln4&p=conjur_main_help&g=1).
  [cyberark/cyberark-conjur-cli#92](https://github.com/cyberark/cyberark-conjur-cli/issues/92)
- Directory structure has been refactored.
  See [design document](https://github.com/cyberark/cyberark-conjur-cli/blob/main/design/general_refactorings.md) for
  more details. This is a breaking change. Users who import the SDK in their projects should change their import
  statement from
  `from conjur.client import Client` to `from conjur.api import Client`
  [cyberark/cyberark-conjur-cli#121](https://github.com/cyberark/cyberark-conjur-cli/issues/121)

## [0.1.1] - 2020-11-05

### Added
- Method `whoami` is now available in both CLI and API (requires Conjur v1.9+).
  [cyberark/cyberark-conjur-cli#68](https://github.com/cyberark/cyberark-conjur-cli/pull/68)

### Changed
- Removed references to `enum.auto` to support Python3.5
  [cyberark/cyberark-conjur-cli#43](https://github.com/cyberark/cyberark-conjur-cli/issues/43)

## [0.1.0] - 2020-01-03

### Added
- Added ability to publish the container to DockerHub
  [cyberark/cyberark-conjur-cli#28](https://github.com/cyberark/cyberark-conjur-cli/issues/28)
- Changed test container to use Ubuntu instead of Alpine

## [0.0.5] - 2019-12-06

### Added
- Added ability to delete
  policies [cyberark/cyberark-conjur-cli#23](https://github.com/cyberark/cyberark-conjur-cli/issues/23)

## [0.0.4] - 2019-11-21

### Fixed
- Fixed overrides handling of `Client` account param
  [cyberark/cyberark-conjur-cli#21](https://github.com/cyberark/cyberark-conjur-cli/issues/21)
- Fixed running of linter due to `cryptography` upstream bug
- Fixed failing tests when running on different OS YAML parsing libraries

## [0.0.3] - 2019-08-20

### Fixed
- Fixed application of conjurrc overrides of `Client` initialization params
  [cyberark/cyberark-conjur-cli#14](https://github.com/cyberark/cyberark-conjur-cli/issues/14)
- Fixed escaping of `/` in parameters of URL

## [0.0.2] - 2019-05-17

### Changed
- Package prefix changed from `conjur_api_python3` to `conjur`
- Bundle name changed from `conjur-api-python` to `conjur-api`
- CLI renamed from `conjur-py3-cli` to `conjur-cli`

### Added
- Support for returning output from policy changes invocations
- Fatal exception is raised when this module is run on Python2

## [0.0.1] - 2019-05-01

### Added
- The first tagged version.

[Unreleased]: https://github.com/cyberark/cyberark-conjur-cli/compare/v7.2.0...HEAD
[7.1.0]: https://github.com/cyberark/cyberark-conjur-cli/compare/v7.1.0...v7.2.0
[7.1.0]: https://github.com/cyberark/cyberark-conjur-cli/compare/v7.0.1...v7.1.0
[7.0.1]: https://github.com/cyberark/cyberark-conjur-cli/compare/v0.1.1...v7.0.1
[0.1.1]: https://github.com/cyberark/cyberark-conjur-cli/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/cyberark/cyberark-conjur-cli/compare/v0.0.5...v0.1.0
[0.0.5]: https://github.com/cyberark/cyberark-conjur-cli/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/cyberark/cyberark-conjur-cli/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/cyberark/cyberark-conjur-cli/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/cyberark/cyberark-conjur-cli/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/cyberark/cyberark-conjur-cli/releases/tag/v0.0.1
