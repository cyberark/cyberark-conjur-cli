# DEPRECATED

As of September 4, 2024 this project is deprecated and will no longer be maintained. Please use [cyberark/conjur-cli-go](https://github.com/cyberark/conjur-cli-go) instead.

# cyberark-conjur-cli

This repository includes self-contained Conjur CLI (`conjur`) for
accessing the Conjur API to manage Conjur resources.

Note: The Conjur Python SDK was removed from this repo and is now maintained in the 
https://github.com/cyberark/conjur-api-python repository

[![Test Coverage](https://api.codeclimate.com/v1/badges/d90d69a3942120b36785/test_coverage)](https://codeclimate.com/github/cyberark/cyberark-conjur-cli/test_coverage) [![Maintainability](https://api.codeclimate.com/v1/badges/d90d69a3942120b36785/maintainability)](https://codeclimate.com/github/cyberark/cyberark-conjur-cli/maintainability)

---

## Certificate level

![](https://img.shields.io/badge/Certification%20Level-Community-28A745?link=https://github.com/cyberark/community/blob/master/Conjur/conventions/certification-levels.md)

This repo is a **Community** level project. It's a community contributed project that **is not reviewed or supported by
CyberArk**. For more detailed information on our certification levels,
see [our community guidelines](https://github.com/cyberark/community/blob/master/Conjur/conventions/certification-levels.md#community)
.

### Using cyberark-conjur-cli with Conjur Open Source

Are you using this project with [Conjur Open Source](https://github.com/cyberark/conjur)? Then we
**strongly** recommend choosing the version of this project to use from the
latest [Conjur OSS Suite release](https://docs.conjur.org/Latest/en/Content/Overview/Conjur-OSS-Suite-Overview.html)
. Conjur maintainers perform additional testing on the Suite release versions to ensure compatibility. When possible,
upgrade your Conjur Open Source version to match the
[latest Suite release](https://docs.conjur.org/Latest/en/Content/ReleaseNotes/ConjurOSS-suite-RN.htm)
. When using integrations, choose the latest Suite release that matches your Conjur Open Source version. For any
questions, please contact us on [Discourse](https://discuss.cyberarkcommons.org/c/conjur/5).

### Supported Services

- Conjur Open Source v1.2.0 or later
- Conjur Enterprise v11.2.1 (v5.6.3) or later

### Supported Platforms

- macOS Catalina or later
- Windows 10 or later
- Red Hat Enterprise Linux 7, 8

### Installation

To access the latest release of the Conjur CLI, go to
our [release](https://github.com/cyberark/cyberark-conjur-cli/releases)
page. For instructions on how to set up and configure the CLI, see
our [official documentation](https://docs.conjur.org/Latest/en/Content/Developer/CLI/cli-lp.htm).

## Usage

For more information on how to set up, configure, and start using the Conjur CLI, see
our [official documentation](https://docs.conjur.org/Latest/en/Content/Developer/CLI/cli-lp.htm).

## Security

When using this CLI on Windows machines, the keyring module used by the CLI will default to 
Enterprise mode. This means that a CLI user who logs in via the CLI will remain logged in
until they explicitly log out. **If using this CLI on Windows, CyberArk recommends that all
users explicitly log out at the end of their session.** This behavior can be changed by 
creating an environment variable called KEYRING_PROPERTY_PERSIST and setting that variable
to 'session' (no quotes). When this variable is set as described, the CLI user should be
logged out when the session expires. 

## Contributing

Instructions for how to deploy a deployment environment and run project tests can be found
in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is [licensed under Apache License v2.0](LICENSE.md). Copyright (c) 2022 CyberArk Software Ltd. All rights
reserved.
