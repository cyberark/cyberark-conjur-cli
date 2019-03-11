# conjur-api-python3

Proof-of-concept Python3-based APIs for Conjur v5

## Building

```
$ ./bin/build
```

## Development

Create a directory that will hold all the virtualenv packages and files:
```
$ python3 -m venv venv
```

Finally, enable your terminal to use those files with this command:
```
$ source venv/bin/activate
```

# Testing

1. Change the login credentials in `test` file
1. Run `./bin/test`
