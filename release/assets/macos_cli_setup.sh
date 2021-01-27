#!/bin/bash -e

USER_PROVIDED_PATH=$1

print_help() {
  cat << EOF

Conjur CLI setup script

Installs and configures the Conjur CLI on macOS environments.
Upon completion of this setup script, you will be able to access the Conjur CLI from anywhere on your machine.
The installation creates a symbolic link between the CLI executable and directory path. By default, this path is '/usr/local/bin'.
To overwrite this path, configure the directory path parameter.

For example ./macos_cli_installation.sh /usr/bin

Usage: ./macos_cli_setup.sh [options]
    -h, --help    Shows this help message

EOF
  exit
}

main() {
  cat << EOF
   ______
  / ____/___  ____    ( )_  ________
 / /   / __ \/ __ \  / / / / // ___/
/ /___/ /_/ / / / / / / /_/ // /
\____/\____/_/ /_/_/ /\____//_/
                /___/
EOF

  if [[ $USER_PROVIDED_PATH = "--help" ]]; then
    print_help
  fi
  executable_path=${USER_PROVIDED_PATH:-'/usr/local/bin'}

  echo "Setting up the Conjur CLI. This will take a few moments...."
  create_symbolic_link $executable_path

  # the first run of the CLI is always the longest. Here we are running the
  # first run of the CLI for the user to hideaway this lag
  conjur --help > /dev/null
  echo "Successfully setup the Conjur CLI. To get started, run 'conjur --help'"
}

# Creates symbolic link to the path of the user's choice. Default location: '/usr/local/bin'
create_symbolic_link() {
  local executable_path=$1
  ln -s -f /$PWD/conjur $executable_path
}

main
