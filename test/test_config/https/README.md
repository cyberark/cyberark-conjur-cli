To regenerate certificates, use [this](https://github.com/conjurdemos/dap-intro/tree/master/tools/simple-certificates)
tool:
```sh-session
$ ./generate_certificates 1 conjur-https
```

Copy the following:
- `certificates/ca-chain.cert.pem` -> `ca.crt`
- `certificates/nodes/conjur-https.mycompany.local/conjur-https.mycompany.local.cert.pem` -> `conjur.crt`
- `certificates/nodes/conjur-https.mycompany.local/conjur-https.mycompany.local.key.pem` -> `conjur.key`
