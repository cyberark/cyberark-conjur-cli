#!/bin/bash -ex

pack_test_runner() {
  pyinstaller -F ${PWD}/test/util/test_runners/integrations_tests_runner.py
}

main() {
  echo "Packing the test runner..."
  pack_test_runner

  echo "Spin up Conjur OSS over HTTPS containers..."
   ./bin/test_integration --process
  cd dist
  echo $(ls)
  cd ..
  echo $(docker ps)
  echo "Run integration tests as a process"
  ./dist/integrations_tests_runner \
    --identifier integration \
    --url https://localhost:8443 \
    --account dev \
    --login admin \
    --password $CONJUR_AUTHN_API_KEY \
    --files-folder /test \
    --cli-to-test dist/conjur
}

main
