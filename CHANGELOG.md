# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Fixed application of conjurrc overrides of `Client` initialization params [#14](https://github.com/cyberark/conjur-api-python3/issues/14)
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

The first tagged version.

[Unreleased]: https://github.com/conjurinc/conjur-api-python3/compare/v0.0.2...HEAD
[0.0.2]: https://github.com/conjurinc/conjur-api-python3/compare/v0.0.1...0.0.2
[0.0.1]: https://github.com/cyberark/conjur-api-python3/tree/v0.0.1
