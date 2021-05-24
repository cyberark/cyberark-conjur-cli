# How to run full integration test suite

The purpose of this document is to detail the steps to run the project's integration tests on each platform we are 
supposed to support. Not all test flows have been integrated to our automated pipeline so it is important to follow this 
guide and understand how to run tests in a semi-automatically fashion.

It is **important** to note that this guide is not strictly for running tests while prepping for a release. This guide 
should be reviewed and the testing process defined here should _not only_ be run before a release, but as you incrementally 
add logic as a sanity-check. That way, if bugs are uncovered, you have enough time to address them!

## Deployment and Setup

Before we can run our integration tests, we need to deploy the required environments and create the test artifact.

At a high level, you will need to:

1. Deploy and configure machines
2. Create a development environment and install requirements
3. Build the `integrations_tests_runner`

#### Deploy and configure machines

You will need 4 different EC2 machines (Windows, RHEL 7, RHEL 8, macOS - if available) for packing the executable. 
If macOS is not available, your local macOS machine should suffice.

#### Create development environment and install requirements

Once those machines are up, clone the repo (`git clone https://github.com/cyberark/conjur-api-python3.git`). You will 
need the repo to build the artifact needed for testing in the upcoming steps.

After you have cloned the repository, you will need to drop into a development environment _and_ install the necessary dependencies
to build the test artifact.

To do both these tasks, follow the instructions outlined [here](https://github.com/cyberark/conjur-api-python3/blob/master/CONTRIBUTING.md#development).

##### Summary:

At the end of this section, you should have:
 1. 4 machines (RHEL 7, 8, Windows, macOS - if available), each with a development environment and requirements installed.

#### Build the `integrations_tests_runner`

The artifact you will build is an executable that wraps the CLI and the integration tests into a single executable.
This allow us to run our integration tests without installing additional dependencies (**including Python**) except for 
what the CLI requires. 

From each machine, inside the development environment you previously created, you will build a test artifact called `integrations_tests_runner`. 
You can build the `integrations_tests_runner` executable by running `pyinstaller -F test/util/test_runners/integrations_tests_runner.py`. 

An artifact will be created as a result and will be saved to the `dist` folder. Hold on to this executable. You will 
need it in the next section. The built executable is not cross-platform so ensure that you repeat this process for 
each of the 4 machines.

## Running tests

The `integrations_tests_runner` artifact should be run on a different machine than the one used to build the executable. "Why" 
you may ask? Because we want to run our tests as close to how our user's would run the CLI (with no Python on the 
machine or any other dependencies used to build the executable).

At a high level, you will need to:

1. Deploy and configure new machines
2. Copy test artifact and test files
3. Run the `integrations_tests_runner`

#### Deploy and configure new machines

You will need to deploy 4 *additional* machines that will be dedicated to running the integration tests (Windows, RHEL 7, 8, 
macOS - if available) and a machine to host your Conjur server (should be Appliance).

#### Copy test artifact and test files

You will need to copy two artifacts to the newly deployed machines that will be used for our tests.

1. The `integrations_tests_runner` executable
2. The test files referenced in the integration tests (policy files, etc). These files live under the `test` 
directory so you will need to just copy the whole `test` directory.

##### Summary:

At the end of this section, you should have:
1. 1 machine to host your Conjur server (should be Appliance)
2. 4 new machines (RHEL 7, 8, Windows, macOS - if available)
3. 4 `integrations_tests_runner` executable with the test files copied to those 4 machines

#### Run the `integrations_tests_runner`

The following is an example of how you would run the `integrations_tests_runner` executable:

```
./integrations_tests_runner \
  --url https://conjur-server \
  --account someaccount \
  --login somelogin \
  --password Myp@SS0rdsS1! \
  --files-folder test
```

Where `url`, `account`, `login`, `password` detail the Conjur server-specific information you previously deployed. The 
type Conjur server deployed impacts where certain tests will pass or fail. For example, if you have configured a Conjur 
server with a verifiable CA-signed certificate, then `test_https_cli_fails_if_cert_is_bad` and 
`test_https_cli_fails_if_cert_is_not_provided` should fail. "Why"? See the developer note above each test 
or see the issue created [here](https://github.com/cyberark/conjur-api-python3/issues/209). For all other flows, these 
tests should pass.

This executable should be 4 times, for each different supported platform.

Congrats! You ran project's integration tests.

## Running tests with configurable environment

As part of our test suite, we also want to test the CLI against different types of Conjur server environments. We want 
to validate the flow when the CLI makes a request to a server and the certificate configured is either 1. a known, 
verifiable CA-signed certificate or 2. a non-verifiable CA-signed certificate.

The second flow (a non-verifiable CA-signed certificate) was already accomplished in the previous steps! 
To accomplish the first flow (a known, verifiable CA-signed certificate ), at a high level, you will need to:

1. Configure the certificate on Conjur server to be known and verifiable
1. Add CA certificate to store
1. Run the `integrations_tests_runner`

#### Configure the certificate on Conjur server to be known and verifiable

On your Conjur server, you will need to create and configure the certificate by following 
[this](https://github.com/cyberark/conjur-api-python3/blob/master/docs/Setting_3rd_party_cert_environment.md) guide.

#### Add CA certificate to store

Python comes with a list of trusted CAs. Every certificate signed by those CAs will be considered trusted and verifiable. 
Those CAs are located in a file called `cacerts.pem`. To manipulate the types of CAs the executable trusts, you will 
need to add the CA pem to that `cacerts.pem` and rebuild the executable. This is exactly what we will do!

1. Choose a platform to run the additional test flow (Hint: macOS should be the easiest). 
1. Locate the path to this file and run `python3 -c "import certifi; print(certifi.where())"`. 
1. Once you have the path, edit the `cacerts.pem` file.
1. Add the CA pem to the top of the file. Adding this CA certificate to the system certificate store allows the 
certificate to be verifiable.

#### Run the `integrations_tests_runner`

Once you have added the CA pem to the `cacerts.pem`, you will need to rebuild the `integrations_tests_runner`. 

1. Remove the cached directories `build` and `dist`.
1. Run `pyinstaller -F test/util/test_runners/integrations_tests_runner.py`. 

Note that for this flow, two tests mentioned in the previous section *should fail*.

For the non-verifiable CA-signed certificate flow, you will need to run through the flow described in this section 
again. All you need to do is:

1. Remove the cached directories.
1. Remove the CA pem from the `cacerts.pem`.
1. Rebuild the `integrations_tests_runner`. 

Note that for this flow, two tests mentioned in the previous section *should pass*.

## Miscellaneous tests - Prerelease

The following section defines tests that should be run shortly before a scheduled release. These tests should be run enough time 
before a release so that if bugs arise, you will have enough time to address them.

There are a couple of manual checks that need to be done in additional to the regular integration tests. For the 
following section, you will need to build the CLI (not the `integrations_test_runner`!) for both RHEL and Windows 
machines.

To do so:

1. On each platform, drop into a development environment and install dependencies as detailed 
[here](https://github.com/cyberark/conjur-api-python3/blob/master/CONTRIBUTING.md#development).
1. Run `pyinstaller -F ./pkg_bin/conjur`. This will build the CLI into an executable.
1. For Windows, sign executable and compress it as zip. For RHEL, just compress the executable as a zip.

#### On Windows machines

Running the compressed and signed executable verifies two things:

1. The final deliverable is a zip file so this ensures that the signed executable doesn't get corrupted during 
compression/decompression 
1. The executable is not flagged as a virus by popular Anti-Virus softwares. For Windows executables, you can upload 
the file to [Virustotal](https://www.virustotal.com/gui/) to verify. In addition to this inital check, copy over the 
CLI to a Windows machine and run it. Running `conjur init` should suffice. If the CLI does not trigger an Anti-Virus 
on the machine, you should be good!

#### On RHEL machines

For RHEL machines, decompressing the CLI and running `conjur init` should suffice. If the CLI runs, you should be good!

#### On macOS machines

For macOS machines, once you have built the .dmg, open it and run the application 
`/Applications/ConjurCLI.app/Contents/Resources/conjur/conjur init`. If the CLI runs, you should be good!
