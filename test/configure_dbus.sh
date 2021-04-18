#!/bin/bash

echo "Configuring D-bus environment"

echo "#!/bin/bash -ex" >> /dbus.sh
echo 'eval "$(dbus-launch --sh-syntax)"' >> /dbus.sh
# Create D-bus keyring directories
mkdir -p ~/.cache
mkdir -p ~/.local/share/keyrings
# Unlock D-bus with empty password
echo "ps -ef | grep dbus | grep -v grep" >> /dbus.sh
echo 'eval "$(echo | gnome-keyring-daemon --unlock)"' >> /dbus.sh
# Export D-bus variables to working shell to support keyring
echo "export DBUS_SESSION_BUS_ADDRESS" >> /dbus.sh
echo "export GNOME_KEYRING_CONTROL" >> /dbus.sh
echo "export SSH_AUTH_SOCK" >> /dbus.sh

if [ "$DEBUG" == "true" ]; then
  echo "bash" >> /dbus.sh
elif [ "$SERVER_MODE" == "appliance" ]; then
  echo "Building the test integration executable..."
#  source /build_integrations_tests_runner
  pyinstaller -D /opt/conjur-api-python3/test/util/test_runners/integrations_tests_runner.py
  echo "python3 /opt/conjur-api-python3/pkg_bin/test_runner.py" >>/dbus.sh
#  echo "bash -c \"nose2 -v -X --config integration_test.cfg -A 'integration'\"" >> /dbus.sh
  _cmd="./dist/integrations_tests_runner/integrations_tests_runner"
  _cmd="$_cmd --url https://$TEST_HOSTNAME"
  _cmd="$_cmd --account $ACCOUNT"
  _cmd="$_cmd --login $LOGIN"
  _cmd="$_cmd --password $ADMIN_PASSWORD"
  _cmd="$_cmd --files-folder /opt/conjur-api-python3/test"

  echo "$_cmd" >> /dbus.sh
else
  echo "bash -c \"nose2 -v -X --config integration_test.cfg -A 'integration'\"" >> /dbus.sh
fi

chmod 755 /dbus.sh

# shellcheck disable=SC2068
exec $@
