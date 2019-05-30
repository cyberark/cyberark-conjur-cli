#!/usr/bin/env python3

# Ensure that we can import the toplevel dir
import sys
sys.path.append(".")
sys.path.append("..")

# Regular imports
import os
import time

import conjur

VARIABLE_PATH = 'a/ b/c'
USE_CONJURRC = True

CONJUR_INFO = {
    'url': "https://conjur.myorg.com",
    'account': "default",
#    'debug': True,
#    'http_debug': False,
}

ACCOUNT_INFO = {
    'ca_bundle': os.path.expanduser(os.path.join("~", "conjur-conjur.pem")),
    'login_id': 'admin',
    'password': 'supersecret',
}

def run():
    client = None
    if USE_CONJURRC is True:
        print("Using conjurrc to log in...")
        client = conjur.Client(**CONJUR_INFO)
    else:
        print("Using username/password combo to log in...")
        client = conjur.Client(**CONJUR_INFO, **ACCOUNT_INFO)

    expected_value = str(time.time()).encode('utf-8')
    print("Setting var '{}' to '{}'...".format(VARIABLE_PATH, expected_value))
    client.set(VARIABLE_PATH, expected_value)

    print("Fetching var '{}'...".format(VARIABLE_PATH))
    actual_value = client.get(VARIABLE_PATH)

    print("Variable value retrieved:", actual_value)

    assert actual_value == expected_value, \
        "ERROR: Values '{}' and '{}' do not match!".format(expected_value, actual_value)

    print("Yay - variable setting and getting worked!")

if __name__ == '__main__':
    run()
