#!/bin/bash

eval "$(dbus-launch --sh-syntax)"
## make bus keyring dirs
mkdir -p ~/.cache
mkdir -p ~/.local/share/keyrings
## Unlock dbus with empty password
ps -ef | grep dbus | grep -v grep
eval "$(echo | gnome-keyring-daemon --unlock)"
## Export dbus variables to working shell to support keyring
export DBUS_SESSION_BUS_ADDRESS
export GNOME_KEYRING_CONTROL
export SSH_AUTH_SOCK
