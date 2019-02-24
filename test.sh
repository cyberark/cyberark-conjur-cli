#!/bin/bash -ex

if [[ "$1" == "-l" ]]; then
  shift
  nose2 -X $@
  exit 0
fi

./build_container.sh

docker run --rm \
           -t \
           -v "$(pwd):/opt/conjur-api-python3" \
           conjur-api-python3-test nose2 -X $@
