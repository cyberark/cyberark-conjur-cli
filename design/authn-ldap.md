# Solution Design - Authn-LDAP Support in CLI

## Table of Contents

- [Solution Design - Authn-LDAP Support in CLI](#solution-design---authn-ldap-support-in-cli)
  - [Table of Contents](#table-of-contents)
  - [Useful Links](#useful-links)
  - [Overview](#overview)
    - [Support in previous CLI versions](#support-in-previous-cli-versions)
    - [Architectural motivation](#architectural-motivation)
  - [Solution](#solution)
    - [User Experience](#user-experience)
      - [Feature Details](#feature-details)
      - [Out of Scope](#out-of-scope)
  - [Performance](#performance)
  - [Backwards Compatibility](#backwards-compatibility)
  - [Affected Components](#affected-components)
  - [Test Plan](#test-plan)
    - [Test Cases](#test-cases)
      - [Unit Tests](#unit-tests)
      - [E2E tests](#e2e-tests)
      - [Security testing](#security-testing)
  - [Logs](#logs)
  - [Documentation](#documentation)
  - [Version update](#version-update)
  - [Security](#security)
  - [Audit](#audit)
  - [Solution Review](#solution-review)

## Useful Links

| Link | Private |
|------|:-------:|
| [Conjur Docs: LDAP Authentication - Overview](https://docs.conjur.org/Latest/en/Content/Integrations/ldap/ldap-sync-authn-integration.htm) | No |
| [Conjur Docs: Configure Developer Environment to Use LDAP Authentication](https://docs.conjur.org/Latest/en/Content/Integrations/ldap/ldap-authn-configure-dev-env.htm) (For Ruby-based) | No |
| [Pseudo-code for AuthenticationStrategy interface](https://gist.github.com/jvanderhoof/c0457452ec83dbf5c31527edfb8c1dcb) | No |

## Overview

Conjur supports various forms of authentication, including LDAP. This document describes the design and implementation of the LDAP authentication
support in the new Python-based Conjur CLI.

### Support in previous CLI versions

In the Ruby-based CLI, it was possible to configure the CLI to use LDAP authentication instead of the default authentication method. This was
done by changing the authn_url configured for the CLI, either in .conjurrc (`authn_url: https://<host>/authn-ldap/<serviceid>`) or by setting the
`CONJUR_AUTHN_URL` environment variable. This worked because the authn-ldap service has the same interface as the default authn service, with the
exception of the service_id which is included in the URL. Therefore it didn't matter to the CLI which method was being used.

However, with the new Python-based CLI, the authn_url is no longer directly configurable. Instead, we store only the Conjur base url (conjur_url)
in .conjurrc and construct the authn_url from that in code. To maintain this paradigm, we need to explicitly specify that we want to use LDAP
when calling the CLI, and have the CLI add the authn-ldap endpoing and service_id to the authn_url.

### Architectural motivation

Another motivation for this change is that we want to add support for all forms of authentication in the various Conjur SDKs. Therefore we want
the conjur-api-python library to be constructed in a way that allows us to easily add support for different authentication methods by
implementing a common `AuthenticationStrategy` interface. Since the CLI and API are now in separate repositories, much of the implementation for
this design will occur in the API, which will move us closer to a pluggable authentication flow.

## Solution

### User Experience

The `conjur init` command should support LDAP authentication. It should be possible to specify the authentication type using the
`-t` or `--authn-type` option. The default value should be `authn` (same as current), and it should additionally support `ldap`.
When using `ldap`, a `--service-id` option should be mandatory.
If the `--service-id` option is specified, then `--authn-type` should default to `ldap`.

| Option | Acceptable Values | Default | Description |
| ------ | ----------------- | ------- | ----------- |
| `--authn-type` / `-t` | `authn`, `ldap` | If `--service-id` is provided: `ldap`. Otherwise `authn` | The authentication method to use when connecting to Conjur |
| `--service-id` | `<service_id>` | N/A | The service_id of the LDAP service to use |

#### Feature Details

##### In the CLI repository

The CLI implementation should be straightforward. It needs to support the new CLI arguments in the `init` command,
and it will need to pass them to the conjur-api-python library.
Code changes will need to be made in the following files (may not be inclusive):

- [conjur/argument_parser/_init_parser.py](../conjur/argument_parser/_init_parser.py)
- [conjur/cli.py](../conjur/cli.py)
- [conjur/cli_actions.py](../conjur/cli_actions.py)

##### In the API repository

Create a new `AuthenticationStrategy` interface that will allow us to abstract the authentication flow. The interface should
take a `CredentialProvider` and Conjur account as inputs, as well as any other arguments that are needed to authenticate,
such as `service_id` for LDAP. The interface should have an `authenticate` method which returns a Conjur auth token. All details of authentication (including `login` for authn and authn-ldap)
should be handled by the `AuthenticationStrategy` interface.

With the new interface, we no longer need to pass a `CredentialsProvider` instance to the `Client` class. Instead, we can pass an
`AuthenticationStrategy` instance which will be used to authenticate and store the credentials in it's own `CredentialsProvider` instance.
When calling the `authenticate` method on the `Client`, we will invoke the `AuthenticationStrategy` and return the auth token.

#### Out of Scope

- Other authentication methods. We would like to add support for all other supported authentication methods to the API in the future.

## Performance

There should be no impact on performance with this change.

## Backwards Compatibility

The interface of the API will not be backwards compatible. Currently the `Client` class takes a `CredentialsProvider` instance as an input,
but going forward it will take an `AuthenticationStrategy` instance instead.

The CLI will be backwards compatible, as this only adds new options.

## Affected Components

- [cyberark/conjur-api-python](https://github.com/cyberark/conjur-api-python)
- [cyberark/cyberark-conjur-cli](https://github.com/cyberark/cyberark-conjur-cli)

## Test Plan

### API

We will need to create new and update existing unit tests in the API for the new authentication flow and the LDAP authentication strategy.

### CLI

We will need to create new and update existing unit tests and integration tests for the new CLI options.

### Test Cases

#### Unit Tests

#### E2E tests

E2E tests are expensive. We should limit E2E testing to happy path "smoke
tests", and leave sad path testing to unit testing and lower level functional
tests.

#### Security testing

Security testing will include:

- Automated Vulnerability scans

## Logs

## Documentation

We will need to update official documentation for the CLI to include the new options for LDAP.

We will also need to update the README for the API repository to include the new authentication flow and the `AuthenticationStrategy` interface.

## Version update

The CLI will need a new minor version, presumably 7.2.0, since this will add new features but not break existing functionality.

Following [Semantic Versioning](https://semver.org/), the API should need a new major version, since this will be a breaking change. However it appears that we're still on [0.0.5](https://github.com/cyberark/conjur-api-python/blob/main/conjur_api/__init__.py#L6) which is a pre-release version, so we should be able to bump the version to 0.0.6 instead.

## Security

This feature will require a security review.

## Audit

No changes to Conjur audit behavior are required for this feature.

##  Development Tasks


| Description | Jira Story | Estimated<br />Story<br />Points<br /> | Completed |
|-------------|------------|-----------|-----------|
| Abstract authentication flow into new interface |[ONYX-20429](https://ca-il-jira.il.cyber-ark.com:8443/browse/ONYX-20429)|4||
| API support for LDAP authentication |[ONYX-20430](https://ca-il-jira.il.cyber-ark.com:8443/browse/ONYX-20430)|2||
| CLI support for LDAP |[ONYX-20431](https://ca-il-jira.il.cyber-ark.com:8443/browse/ONYX-20431)|3||
| Security review for LDAP auth support |[ONYX-20432](https://ca-il-jira.il.cyber-ark.com:8443/browse/ONYX-20432)|1||
| Update API readme for new authentication flow |[ONYX-20433](https://ca-il-jira.il.cyber-ark.com:8443/browse/ONYX-20433)|1||
| Work with TW to update CLI docs for LDAP support |[ONYX-20434](https://ca-il-jira.il.cyber-ark.com:8443/browse/ONYX-20434)|2||

## Solution Review

<table>
<thead>
<tr class="header">
<th><strong>Persona</strong></th>
<th><strong>Name</strong></th>
<th><strong>Design Approval</strong></th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td>Team Leader</td>
<td>John Tuttle</td>
<td><ul>
<p> </p>
</ul></td>
</tr>
<tr class="even">
<td>Product Owner</td>
<td>Jane Simon</td>
<td><ul>
<p> </p>
</ul></td>
</tr>
<tr class="odd">
<td>System Architect</td>
<td>Jason Vanderhoof</td>
<td><ul>
<p> </p>
</ul></td>
</tr>
<tr class="even">
<td>Security Architect</td>
<td>Andy Tinkham</td>
<td><ul>
<p> </p>
</ul></td>
</tr>
<tr class="odd">
<td>QA Architect</td>
<td>Adam Ouamani</td>
<td><ul>
<p> </p>
</ul></td>
</tr>
</tbody>
</table>
