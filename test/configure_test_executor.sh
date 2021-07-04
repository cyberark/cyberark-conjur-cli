#!/bin/bash

###########################################################
# Docker image entry point script                         #
# Generates the script that configures DBUS and runs the  #
# tests according the SERVER_MODE (appliance/oss)         #
###########################################################

script_file=/tests_executor.sh

mkdir -p ~/.cache
mkdir -p ~/.local/share/keyrings

# Write the tests runner script that configures DBUS and runs
# the tests.
cat > $script_file <<'endmsg'
#!/bin/bash -ex

eval "$(dbus-launch --sh-syntax)"
ps -ef | grep dbus | grep -v grep
eval "$(echo | gnome-keyring-daemon --unlock)"
export DBUS_SESSION_BUS_ADDRESS
export GNOME_KEYRING_CONTROL
export SSH_AUTH_SOCK

endmsg

# When the tests are running against appliance the
# tests are running using test integration executable.
# The function builds the test integration executable command
function _tests_runner_cmd() {
  local _cmd="./dist/integrations_tests_runner"
    _cmd="$_cmd --url https://$TEST_HOSTNAME"
    _cmd="$_cmd --account $ACCOUNT"
    _cmd="$_cmd --login $LOGIN"
    _cmd="$_cmd --password $ADMIN_PASSWORD"
    _cmd="$_cmd --files-folder /opt/conjur-api-python3/test"
  echo "$_cmd"
}

# Appends the 1st argumnet to the script file
function append_to_file() {
  echo "$1" >> $script_file
}

if [ "$DEBUG" == "true" ]; then
  echo "bash" >> $script_file
elif [ "$SERVER_MODE" == "appliance" ]; then
    echo "Running testing against $SERVER_MODE. Building the test integration executable..."
    # Add tests runner executable command
    source /build_integrations_tests_runner
    # The '_tests_runner_cmd' contains the admin password so we don't want to print it to the log
    append_to_file "set +x"
    append_to_file "$(_tests_runner_cmd)"
    append_to_file "set -x"
else
  # Server mode is Conjur OSS
  # Add nose2 command
  append_to_file "bash -c \"nose2 -v -X --config integration_test.cfg -A 'integration'\""
fi

chmod 755 $script_file

# exec "$@" is typically used to make the entrypoint a pass through that then runs the docker command
exec $@
