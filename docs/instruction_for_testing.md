# Running tests before release

The purpose of this document is to detail the steps to take to properly run the CLI integration tests on each supported platform. Not all test flows have been integrated in our automated pipeline so it is important to understand how to run tests in a semi-automatically fashion.

It is **important** to note that this guide is not strictly for running tests while prepping for a release. This guide should be reviewed and the testing process defined here should be run a few weeks before a release, as you incrementally add logic. That way, if bugs are uncovered, you have enough time to address them!

## Deployment and Setup

Before we can run our integration tests, we need to deployment the required environments and create the necessary artifacts.

At a high level, you will need to:

1. Deploy and configure machines
1. Clone the CLI/SDK repository
1. Install dependencies on those machines
1. Build the `integrations_tests_runner`

#### Deploy and configure machines

You will need a machine to host your Conjur server (should be Appliance) and 4 different EC2 machines (Windows, RHEL 7, RHEL 8, macOS - if available) for packing the executable. If macOS is not available, your local macOS machine should suffice.

On your Conjur server, you will need to create and configure the certificate on the server by following this walk-through guide (TODO ADD LINK), stoping at the section titled *Build CLI with your CA included*. This will come in handy in the following sections when we validate the different certificate flows.

#### Build the test runner

The test runner executable wraps the CLI and the integration tests into a single executable, allowing us to run our integration tests without installing additional dependencies except for what the CLI requires. For more information see [here](https://github.com/cyberark/conjur-api-python3/blob/master/CONTRIBUTING.md#running-tests-outside-of-a-containerized). 

On those machines intended to pack the `integrations_tests_runner`, you will need to drop into a virtual environment and install dependencies. Follow the instructions [here](https://github.com/cyberark/conjur-api-python3/blob/master/CONTRIBUTING.md#development) for how to do this. Once you have done this, run: `pyinstaller -F test/util/test_runners/integrations_tests_runner.py`. 

An artifact will be created as a result of running this command and will be saved to the `dist` folder. Hold on to this executable. You will need it in the next section.

## Running tests

The `integrations_tests_runner` should be run on a different machine than the one used to build the executable. "Why" you may ask? Because we want to run our tests as close to how our user's would run the CLI (with no Python on the machine or any other dependencies used to build the executable).

At a high level, you will need to:

1. Deploy 4 *additional* machines that will be dedicated to running the integration tests (Windows, RHEL 7, RHEL 8, macOS - if available)
1. Copy over the `integrations_tests_runner` executable to the new machines
1. Copy over the artifacts referenced in the integration tests to the new machines. These artifacts live under the `test` directory so just copy the whole `test` directory.
1. Run the executable

The following is an example of how you would run the `integrations_tests_runner` executable:

```
./integrations_tests_runner \
  --url https://conjur-server \
  --account someaccount \
  --login somelogin \
  --password Myp@SS0rdsS1! \
  --files-folder test
```

Where `url`, `account`, `login`, `password` detail the Conjur server-specific information you previously deployed. Depending on the type of Conjur server you deployed, two tests should fail. For example, if you have configured a Conjur server with a verifiable CA-signed certificate, then `test_https_cli_fails_if_cert_is_bad` and `test_https_cli_fails_if_cert_is_not_provided` should fail. "Why" you may ask? See the developer note above each test or see the issue created [here](https://github.com/cyberark/conjur-api-python3/issues/209). For all other flows, these tests should pass.

Congrats! You ran project's integration tests.

## Running tests with configurable environment

As part of our test suite, we also want to test the CLI against different types of Conjur server environments. We want to validate the flow when the CLI makes a request to a server and the certificate configured is either 1. a known, verifiable CA-signed certificate or 2. a non-verifiable CA-signed certificate.

Python comes with a list of trusted CAs. Every certificate signed by those CAs will be considered trusted certificate. Those CAs are located in a file called `cacerts.pem`. To get the path to this file, run in `python3 -c "import certifi; print(certifi.where())"`

At a high level, you will need to:

1. Pick a platform to run the additional test flow (Hint: macOS should be the easiest)
1. Complete the walk-through doc  (TODO ADD LINK) for configuring a certificate starting at the *Build CLI with your CA included* section.
1. Once you have built the `integrations_tests_runner` with a verifiable CA-signed certificate, run the `integrations_tests_runner` executable one last time. The two tests mentioned in the previous section should fail.

Note that you should remove the `build` and `dist` directories to make sure you build a fresh executable!

## Miscellaneous tests

There are a couple of manual checks that need to be done in additional to the regular integration tests.

You should compress the *signed* Windows CLI executables (not the `integrations_test_runner`!) and run it on a Windows machine. 

This will verify two things:

1. The executable doesn't get corrupted during compression/decompression 
1. The executable is not flagged as a virus by popular Anti-Virus softwares. For Windows machines, you can build the CLI (not the `integrations_test_runner`!) and upload the file to [Virustotal](https://www.virustotal.com/gui/) to verify. In addition to this inital check, copy over the CLI to a Windows machine and run it. Running `conjur init` should suffice.

