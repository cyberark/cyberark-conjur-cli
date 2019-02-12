#!/usr/bin/env python3

import os
import time

import conjur_api_python3 as conjur

VARIABLE_PATH='a/ b/c'

def run():
    ca_bundle = os.path.expanduser(os.path.join("~", "conjur-conjur.pem"))
    client = conjur.Client(url="https://conjur.myorg.com",
                           ca_bundle=ca_bundle,
                           account="myorg",
                           login_id='admin',
                           password='supersecret',
                           debug=False,
                           ssl_verify=True)

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
