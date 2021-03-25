#!/bin/bash
## dbus command running in .bashrc allow us to export the variables to current session
# Running eval to start dbus
#echo 'eval "$(dbus-launch --sh-syntax)"' > ~/.bashrc
# make bus keyring dirs
#mkdir -p ~/.cache
#mkdir -p ~/.local/share/keyrings
# Unlock dbus with empty password
#echo 'eval "$(echo | gnome-keyring-daemon --unlock)"' >> ~/.bashrc
# Export dbus variables to working shell to support keyring
#echo "export DBUS_SESSION_BUS_ADDRESS" >> ~/.bashrc
#echo "export GNOME_KEYRING_CONTROL" >> ~/.bashrc
#echo "export SSH_AUTH_SOCK" >> ~/.bashrc


#
echo 'eval "$(dbus-launch --sh-syntax)"' > /dbus.sh
## make bus keyring dirs
mkdir -p ~/.cache
mkdir -p ~/.local/share/keyrings
## Unlock dbus with empty password
echo 'ps -ef | grep dbus | grep -v grep' >> /dbus.sh
echo 'eval "$(echo | gnome-keyring-daemon --unlock)"' >> /dbus.sh
## Export dbus variables to working shell to support keyring
echo "export DBUS_SESSION_BUS_ADDRESS" >> /dbus.sh
echo "export GNOME_KEYRING_CONTROL" >> /dbus.sh
echo "export SSH_AUTH_SOCK" >> /dbus.sh

echo "bash -c \"nose2 -v -X --config integration_test.cfg -A 'integration'\"" >> /dbus.sh
#echo "nose2 -v -X --config integration_test.cfg -A 'integration'" >> /dbus.sh


chmod 755 /dbus.sh

# shellcheck disable=SC2068
exec $@
