USER_PROVIDED_PATH=$1

print_help() {
  cat << EOF

Conjur CLI setup script

Installs and configures the Conjur CLI on macOS environments.
Upon completion of this setup script, you will be able to access the Conjur CLI from anywhere on your machine.
The installation creates a symbolic link between the CLI executable and directory path. By default, this path is '/usr/local/bin'.
To overwrite this path, configure the directory path parameter. For example '$0 /usr/bin'

Usage: $0 [options]
    -h, --help    Shows this help message

EOF
  exit
}

# Creates symbolic link to the path of the user's choice. Default location: '/usr/local/bin'
create_symbolic_link() {
  local executable_path=$1
  # Get relative from where the script is being run
  relative_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
  ln -s -f /$relative_path/conjur $executable_path
  if [ $? -ne 0 ]; then
    echo "Error: Unable to create symbolic link between the provided path and the Conjur executable. Ensure that the provided paths exist."
    exit 1
  fi
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
  if [[ $USER_PROVIDED_PATH = "--help" || $USER_PROVIDED_PATH = "-h" ]]; then
    print_help
  fi
  executable_path=${USER_PROVIDED_PATH:-'/usr/local/bin'}

  if [[ ! -d "/usr/local/bin" ]]; then
    echo "The default directory '/usr/local/bin' does not exist or you do not have permissions to access it." \
    "Provide the path to the user directory to create the symbolic link. For example: '$0 /usr/bin'."
    exit 1
  fi

  echo "Setting up the Conjur CLI. This will take a few moments...."
  create_symbolic_link $executable_path

  # The first run of the CLI is always the longest. Here we are running the
  # first run of the CLI for the user to hideaway this lag
  conjur --help > /dev/null
  if [ $? -ne 0 ]; then
    echo "Error: The Conjur CLI executable was not found in the current directory."
    exit 1
  fi
  echo "Successfully setup the Conjur CLI. To get started, run 'conjur --help'"
}

main
