# Release Automation

This document is the design document for automating our release process for the Python CLI/SDK project. We have a requirement to support four different platforms (RHEL 7/8, macOS, and Windows) and need to create automated flows for each of them. 

#### Milestone 1

1. Spin up 4 machines/containers, pack the CLI executable, and add to artifacts of the build
   -  The artifacts will be used for testing

#### Milestone 2

1. Run the integration tests on those machines as part of our pipeline. We want to run the tests on new machines that don't have Python or any other dependencies to ensure our tests accurately represent user environments.
2. Run integration tests against older Conjur servers (Conjur enterprise v5.6.3 and Conjur OSS v1.2.0).
3. Run integration tests against different types of Conjur environment configurations (CA-signed certificate, self-signed certificate, unknown CA-signed certificate).

#### Milestone 3

1. Add a security scan as part of the pipeline, adding the report to the artifact tab of the build. We can utilize the open source version to generate a report.
1. Versioned tags trigger a draft release. Currently, not possible to attach the release artifacts to the release because they need to be signed which needs to be manual process.

### RHEL 8

#### Current proposal

1. Spin up a RHEL 8 agent/container
1. Install dependencies (Python, Pip3, Pyinstaller) on that container
1. Pack the CLI and test runner on the RHEL agent/container
1. Deploy Conjur and a new container to run the integration tests against the newly built CLI executable

##### Known issues with proposal

Receiving a `OpenSSL internal error: FATAL FIPS SELFTEST FAILURE` error. In our Jenkins pipeline we have RHEL machines that are FIPS enabled so all executables that run on those machines need to also be. The CLI executable is not FIPS compliant.

##### Suggestion to overcome issue

Even though users deploy the CLI from outside of a Dockerized environment, containers are abstractions that give us consistent runtime environments. Therefore, to overcome this limitation I suggest we deploy two containers 1. a container to run the integration tests 2. a container that will have Conjur / Conjur enterprise deployed.

### RHEL 7

Same flow as above

Open questions:

1. Do we have a RHEL 7 agent available?

### Windows

#### Current proposal

1. Spin up a Windows agent and a Windows container
1. Install dependencies (Python, Pip3, Pyinstaller) on the container
1. Pack the CLI and test runner on the Windows agent/container
1. Deploy Conjur and a new container to run the integration tests against the newly built CLI executable

#### Backup plan:

Use Github Actions. A couple of problems with this:

1. Our integration testing process will be divided which makes it harder to focus
1. If we choose to run our tests against a Conjur server that sits in AWS, we cannot push connection details to the Github actions

### macOS

#### Current proposal

1. Spin up a macOS agent (*not currently available*) and a macOS container
1. Install dependencies (Python, Pip3, Pyinstaller) on the container
1. Pack the CLI and test runner on the macOS agent/container
1. Deploy Conjur and a new container to run the integration tests against the newly built CLI executable

#### Failed attempts

1. Github actions. Attempt at installing Docker in a macOS runner was not successful.

### Signing

As part of the release process, we require that our zips aer signed before being delivered to users. This process will need to remain a manual one because our signing tool has not yet been integrated to our corp Jenkins pipelines. Additionally, macOS requires us to sign and notarize our executables to be given "verified developer" status. This process is not yet fully defined in our organization so we cannot automate this yet.

### Complications

We have different environments we need to run our tests against. Before we can release, we need to run our integration tests against different Conjur server configurations:

1. Self-signed certificate
1. Unknown CA-signed certificate
1. A CA-signed certificate - anticipating this to be challenging. This is currently achieve in AWS by configuring the certificate at the Load Balancer level.

How can we configure these different environments in Docker containers without having to deploy machines in AWS? Would it be bad practice/not sustainable to leave these AWS machines up constantly?