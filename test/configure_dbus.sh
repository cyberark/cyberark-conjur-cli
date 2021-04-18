#!/bin/bash

echo "Configuring D-bus environment"

echo "#!/bin/bash -ex" >> /dbus.sh
echo "# D-bus environment script" >> /dbus.sh
echo "echo ->0" >> /dbus.sh
echo 'eval "$(dbus-launch --sh-syntax)"' >> /dbus.sh
echo "echo ->1" >> /dbus.sh
# Create D-bus keyring directories
mkdir -p ~/.cache
mkdir -p ~/.local/share/keyrings
# Unlock D-bus with empty password
echo "ps -ef | grep dbus | grep -v grep" >> /dbus.sh
echo "echo ->2" >> /dbus.sh
echo 'eval "$(echo | gnome-keyring-daemon --unlock)"' >> /dbus.sh
echo "echo ->3" >> /dbus.sh
# Export D-bus variables to working shell to support keyring
echo "export DBUS_SESSION_BUS_ADDRESS" >> /dbus.sh
echo "export GNOME_KEYRING_CONTROL" >> /dbus.sh
echo "export SSH_AUTH_SOCK" >> /dbus.sh
echo "echo ->4" >> /dbus.sh
if [ "$DEBUG" == "true" ]; then
  echo "bash" >> /dbus.sh
elif [ "$SERVER_MODE" == "appliance" ]; then
  echo "Building the test integration executable..."
  source /build_integrations_tests_runner

  echo "openssl version -a" >> /dbus.sh

  echo "Write the test integration executable command to script..."
  _cmd="./dist/integrations_tests_runner"
  _cmd="$_cmd --url https://$TEST_HOSTNAME"
  _cmd="$_cmd --account $ACCOUNT"
  _cmd="$_cmd --login $LOGIN"
  _cmd="$_cmd --password $ADMIN_PASSWORD"
  _cmd="$_cmd --files-folder /test"
  echo cmd: "$_cmd"


  echo "$_cmd" >> /dbus.sh
  echo "echo ->5" >> /dbus.sh
  echo "echo running tests completed..." >> /dbus.sh
  echo "echo ->6" >> /dbus.sh
  echo 'cat dbus.sh file...'
  cat /dbus.sh
else
  echo "bash -c \"nose2 -v -X --config integration_test.cfg -A 'integration'\"" >> /dbus.sh
fi

chmod 755 /dbus.sh

# shellcheck disable=SC2068
exec $@
