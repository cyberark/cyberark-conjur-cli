#  **Dockerless CLI -** deployment

This document is the design document for the deployment of the Python CLI. 

Currently, our Python CLI can be deployed in the following ways:

1. Install the CLI via the pip Python package manager like so: `pip3 install conjur-client`. **Python is required** on
machine if installing the CLI in this way. If installed via pip, the user can then run the CLI like so `conjur-cli --help`

2. Install and run the executable (**Python is** **not** required on the machine)

   The CLI is delivered as a standalone executable, packed with the required runtime and dependencies (excluding a few
   base linked libraries that are expected on the system). Therefore, there is no need for Python or other prerequisites
   to be installed on machine. The executable can be fetched by navigating to our
   [Python CLI release page](https://github.com/cyberark/cyberark-conjur-cli/releases/tag/v0.0.5).
   
   If installed in this manner the CLI can be invoked by, `./python-cli-executable-location variable get ...`

### Design

#### Pip3 package

We make CLI package available to the public by pushing to a public repository called PyPi. We will maintain pushing our
the Python CLI to pip3 for both customer's machines have internet access and for our development work.

Our Python API is also delivered this way and PyPi is the main installation method for it so this should be retained.
The infrastructure is already in-place so this would be at no additional effort.

#### Standalone executable

To install the executable, for Linux and macOS machines we will provide tar.gz files. For Windows machine we will
provide a zip file that will be available on the [release page](https://github.com/cyberark/cyberark-conjur-cli/releases)
of our Github repository.

tar.gz is a standard archieve format for macOS and other Linux systems and has been used to deliver software in
[another one of our open source projects](https://github.com/cyberark/secretless-broker/releases/tag/v1.7.1). tar.gz
is a better solution than zip for Linux and macOS machines because zip's complement, unzip, does not come packaged in
the common distributions (RHEL for example). This would require that users install unzip on their machines to use our
software which should be avoided. We want to use tar.gz because it is usable without needing any additional software
as unzip would demand. Each achived file will have its respective executable as detailed below.

```bash
conjur-cli-linux.tar.gz
	conjur
conjur-cli-darwin.tar.gz
  conjur
conjur-cli-windows.zip
  conjur.exe
```

Once the user has installed the archive file, they will need to extract the contents by running
`tar -xf conjur-cli-linux.tar.gz`

Once they do this, they can run the newly extracted executable in one of the following ways:

1. Run the executable from where the extraction took place like so: `./conjur --help` 
2. Move the executable  (`conjur`) to their `/usr/local/bin` path so that it would look something like
`/usr/local/bin/conjur`. An additional option would be having the user add it to their `PATH`. That way, the CLI
executable will be available from anywhere on their machine without having to detail the full path. The exact location
is left up to the user but we can provide a recommendation

### Delivery

At this time, the packing the CLI into an executable will be a manual process. We need to support RHEL, Windows, and
macOS machines so we will manually spin up VMs (for RHEL and Windows) and manually pack the CLI:
`pyinstaller --onefile pkg_bin/conjur`. On macOS we will pack locally.

Once we have manually packed the executable and are ready for release, we will manually push the executables to the
repo's release page.

#### Upgrade from Ruby to Python CLI

For all customers who have installed the Ruby CLI gem, we will request that the customer either remove it or rename it.
They can do so doing the following:

1. Run `which conjur` and they will get the path of the gem. For example `/Users/myuser/.rvm/gems/ruby-2.x.x/bin/conjur`
2. Rename the gem found in that path to `/Users/myuser/.rvm/gems/ruby-2.x.x/bin/conjur.v6`

### Testing

A full test plan will be provided in a separate document in this repo. 

### Helpful resources

If in further phases we need to sign the files, see how to for macOS
[here](https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Win-Code-Signing) and here
for [Windows](https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Win-Code-Signing).

### Open questions

1. Do we need to sign both the zip and the executables? Not for phase one.

### Delivery plan

1. Implement changes outlined in the design (*3 days*)
   1. Update executable and package name
2. Map out the manual tests *(1 days)*
3. Create documentation in `README.md` of the repository *(1 days)*
4. Write draft document for TW for online help and open a docs ticket for TW *(2 days)*

Total 7 days

