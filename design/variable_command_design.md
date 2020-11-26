# Dockerless CLI - `variable` action

This document is the design document for the variable CLI command for the Dockerless project. The functionality for the variable CLI command already exists so all that is left is the following:

1. Ensure UTs and integration tests exist and are GA quality
3. Write proper documentation in `README.md` of the repository

For the full UX design for the list command see [here](https://ljfz3b.axshare.com/#id=yokln4&p=conjur_main_help&g=1).

### UX mapping

We use a third-party module called [argparse](https://docs.python.org/3/library/argparse.html) which gives us limited control over the types of errors we can return. Therefore, at this time we will not surgicially change the errors and leave them as is. The following is a mapping of the current flow for all possible permutations of the variable CLI command and their expected outputs/behavior. 

*Input for variable is neither get/set*

```bash
$ conjur-cli variable boo

## Current
usage: conjur-cli variable [-h] {get,set} ...
conjur-cli variable: error: argument action: invalid choice: 'boo' (choose from 'get', 'set')

## Should be
conjur-cli variable: error: argument action: invalid choice: 'boo' (choose from 'get', 'set')

<Variable command help screen>
```

*One of the batch secrets doesn’t have value/doesn’t exist*

```bash
$ conjur-cli variable get secrets/test_secret foo/bar

## Current
requests.exceptions.HTTPError: 404 Client Error: Not Found for url: https://localhost/secrets/myorg/variable/secrets%2Ftest_secret%2Cfoot%2Fbar

## Should be
Error: Data either not found or variable value does not exist

<Variable command help screen>
```

*Set secrets*

```bash
$ conjur-cli variable set foo/bar mysecret

## Current
Value set: 'foo/bar'

## Should be
Success! Data set to: 'foo/bar'
```

*Get secrets*

```bash
$ conjur-cli variable get foo/bar
mysecret%
```

*Get a secret without inputting which secret to get*

```bash
$ conjur-cli variable get __

## Current 
usage: conjur-cli variable get [-h] variable_id [variable_id ...]
conjur-cli variable get: error: the following arguments are required: variable_id

## Should be
conjur-cli variable get: error: the following arguments are required: variable_id

<Variable command help screen>
```

*Get a secret without inputting which variable_id / its value*

```bash
$ conjur-cli variable set __ __

## Current
usage: conjur-cli variable set [-h] variable_id value
conjur-cli variable set: error: the following arguments are required: variable_id, value

## Should be
conjur-cli variable set: error: the following arguments are required: variable_id, value

<Variable command help screen>
```

*Get secret without inputting the variable_id’s value*

```bash
$ conjur-cli variable set foo/bar __

## Current
usage: conjur-cli variable set [-h] variable_id value
conjur-cli variable set: error: the following arguments are required: value

## Should be
conjur-cli variable set: error: the following arguments are required: value

<Variable command help screen>
```

*Get secrets with more inputs than excepted*

```bash
$ conjur-cli variable set foo/bar mysecret extraargument

## Current
usage: conjur-cli [-h] [-v] [-l URL] [-a ACCOUNT] [-c CA_BUNDLE] [--insecure] [-u LOGIN_ID] [-k API_KEY] [-p PASSWORD] [-d]
         [--verbose]
         {list,variable,policy} ...
conjur-cli: error: unrecognized arguments: extraargument

## Should be:
conjur-cli: error: unrecognized arguments: extraargument

<Variable command help screen>
```

*Edge case: spaces in variable_ids*

```bash
conjur-cli variable get "secrets/test with space" foo/bar
{
    "foo/bar": "mysecret",
    "secrets/test with space": "mysecrettwo"
}
```

Notice the `""` that needs to surround variable_ids that have spaces in them to work properly

### Test plan

A full test plan will be provided in a separate document in this repo. 

### Delivery plan

1. Ensure UTs and integration tests exist and are GA quality (3 days)
   1. Sit with QA to map out current tests and what is missing
   2. Implement missing tests (if required)
3. Write and get approval on UX logs (2 days)
4. Write proper documentation in `README.md` of the repository *(1 day)*
5. Write draft document for TW for online help and open a docs ticket for TW *(2 days)*

Total 11 days. Note this is not 11 days of consecutive work. There will be days of waiting for feedback and reviews.