#!/bin/bash -e

docker build -f Dockerfile.test \
             -t conjur-api-python3-test \
             .
