#!/bin/bash
## dbus command runing in .bashrc allow us to export the variables to currnet session
# runing eval cmd to start dubs
echo 'eval "$(dbus-launch --sh-syntax)"' > ~/.bashrc
# make bus keyring dirs
mkdir -p ~/.cache
mkdir -p ~/.local/share/keyrings
# unlock bus
echo 'eval "$(echo | gnome-keyring-daemon --unlock)"' >> ~/.bashrc
# Export dbus variables to working shell to support keyring
echo "export DBUS_SESSION_BUS_ADDRESS" >> ~/.bashrc
echo "export GNOME_KEYRING_CONTROL" >> ~/.bashrc
echo "export SSH_AUTH_SOCK" >> ~/.bashrc
exec $@