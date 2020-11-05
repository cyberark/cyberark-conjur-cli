# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## Unreleased

## [0.1.1] - 2020-11-05

### Added
- Method `whoami`is now availabe in both CLI and API (requires Conjur v1.9+).
  [cyberark/conjur-api-python3#68](https://github.com/cyberark/conjur-api-python3/pull/68)

### Changed
- Removed references to `enum.auto` to support Python3.5 [#43](https://github.com/cyberark/conjur-api-python3/issues/43).

## [0.1.0] - 2020-01-03
### Added
- Added ability to publish the container to DockerHub [#28](https://github.com/cyberark/conjur-api-python3/issues/28)
- Changed test container to use Ubuntu instead of Alpine

## [0.0.5] - 2019-12-06

### Added
- Added ability to delete policies [#23](https://github.com/cyberark/conjur-api-python3/issues/23)

## [0.0.4] - 2019-11-21

### Fixed
- Fixed overrides handling of `Client` account param [#21](https://github.com/cyberark/conjur-api-python3/issues/21)
- Fixed running of linter due to `cryptography` upstream bug
- Fixed failing tests when running on different OS YAML parsing libraries

## [0.0.3] - 2019-08-20

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
### Added
- The first tagged version.

[Unreleased]: https://github.com/conjurinc/conjur-api-python3/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/conjurinc/conjur-api-python3/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/conjurinc/conjur-api-python3/compare/v0.0.5...v0.1.0
[0.0.5]: https://github.com/conjurinc/conjur-api-python3/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/conjurinc/conjur-api-python3/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/conjurinc/conjur-api-python3/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/conjurinc/conjur-api-python3/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/cyberark/conjur-api-python3/releases/tag/v0.0.1
