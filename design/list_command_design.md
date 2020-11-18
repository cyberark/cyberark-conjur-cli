# Dockerless CLI - `list` action

This document is the design document for the *list* CLI command for the Dockerless project. The main functionality for the list CLI command has been implemented. Now all that is left is to implement the following flags:

1. `-i, --inspect`
2. `-k, --kind`
3. `-l, --limit`
5. `-r, --role`
6. `-s, --search`
6. `-o, --offset` (low in priority)

`offset` is at a lower priority because the current Ruby CLI does not implement this flag.

In additional to implementing the above flags, we will need to also address the following:

1. Ensure UTs and integration tests exist and are GA quality
3. Write proper documentation in `README.md` of the repository

For the full UX design for the list command see [here](https://ljfz3b.axshare.com/#id=yokln4&p=conjur_main_help&g=1).

### UX mapping

We use a third-party module called [argparse](https://docs.python.org/3/library/argparse.html) which gives us limited control over the types of errors we can return. Therefore, at this time we will not surgicially change the errors and leave them as is. The following is a mapping of the current flow for all possible permutations of the *list* CLI command and their expected outputs/behavior. 

*When no values were found*

```bash
$ conjur-cli list

## Current
[]

## Should be
No results found
```

*List with more inputs than excepted*

```bash
$ conjur-cli list unknown

## Current
usage: conjur-cli [-h] [-v] [-l URL] [-a ACCOUNT] [-c CA_BUNDLE] [--insecure] [-u LOGIN_ID] [-k API_KEY] [-p PASSWORD] [-d]
         [--verbose]
         {list,variable,policy} ...
conjur-cli: error: unrecognized arguments: boo

## Should return an error
```

*Mispell list command*

```bash
$ conjur-cli listboo

## Current
usage: conjur-cli [-h] [-v] [-l URL] [-a ACCOUNT] [-c CA_BUNDLE] [--insecure] [-u LOGIN_ID] [-k API_KEY] [-p PASSWORD] [-d]
                  [--verbose]
                  {list,variable,policy} ...
conjur-cli: error: argument resource: invalid choice: 'listboo' (choose from 'list', 'variable', 'policy')

## Should be:
conjur-cli: error: argument resource: invalid choice: 'listboo' (choose from 'list', 'variable', 'policy')

<Main help screen>
```

*Help flag*

```bash
$ conjur-cli list --help

## Current
usage: conjur-cli list [-h]

optional arguments:
  -h, --help  show this help message and exit
  
## Should be
<List help screen>
```

*`--inspect` should show full object information*

```bash
$ conjur-cli list --inspect
[
		"policy_versions": [
   	 {
      "version": 1,
      "created_at": "2020-11-17T12:46:51.070+00:00",
      "policy_text": "- !policy\n  id: foo\n  body:\n    - &variables\n      - !variable bar \n",
      "policy_sha256": "4b6fd7cfc622dd8790fd437390f5b079c0cd77e72aa862384c5b740bdcedb3c6",
      "finished_at": "2020-11-17T12:46:51.311+00:00",
      "client_ip": "172.17.0.1",
      "id": "myorg:policy:root",
      "role": "myorg:user:admin"
    	},
   	]
  {
    "created_at": "2020-11-18T12:00:00.078+00:00",
    "id": "myorg:variable:secrets/test_secret",
    "owner": "myorg:policy:secrets",
    "policy": "myorg:policy:root",
    "permissions": [

    ],
    "annotations": {
    },
    "secrets": [
      {
        "version": 1,
        "expires_at": null
      }
    ]
  },
  {
    "created_at": "2020-11-18T14:46:17.172+00:00",
    "id": "myorg:user:boo",
    "owner": "myorg:user:admin",
    "policy": "myorg:policy:root",
    "permissions": [

    ],
    "annotations": {
    },
    "restricted_to": [

    ]
  }
]
```

*`--kind=user` gives use all user kinds*

```bash
conjur list --kind=user
[
  "myorg:user:boo"
]
```

*`-k user` gives use all user kinds*

```bash
conjur list -k user
[
  "myorg:user:boo"
]
```

*`--kind=user` gives us no user if no hosts exist*

```bash
conjur list --kind=user
[

]
```

*`--kind=boo` gives us no nothing if no that kind doesn't exist*

```bash
conjur list --kind=boo
[

]
```

*`--limit=4` returns top 4 from the list*

```bash
$ conjur list --limit=4
[
  "myorg:policy:foo",
  "myorg:policy:root",
  "myorg:policy:secrets",
  "myorg:policy:users"
]
```

*`-l 4` returns top 4 from the list*

```bash
$ conjur list -l 4
[
  "myorg:policy:foo",
  "myorg:policy:root",
  "myorg:policy:secrets",
  "myorg:policy:users"
]
```

*`--limit=-1` (negative number or 0) gives us the full list.* In the Ruby CLI, this is an 500 Internal Server Error

```bash
$ conjur list --limit=-1

conjur-cli: error: limit value must be greater than 0
```

*User impersonation with user who doesn't exist*. See question about this in the Open Questions section below.

```bash
$ conjur list --role=myorg:user:boo
Error: 403 Forbidden

<List help screen>
```

*User impersonation with user who exists but doesn't have permissions on any variables*

```bash
$ conjur list --role=myorg:user:foo
[

]
```

*User impersonation with user who exists but has permissions on a single variable*

```bash
$ conjur list --role=myorg:user:bar
[
	"myorg:variable:secrets/test_secret"
]
```

*Stacking flags*

```bash
$ conjur list --role=myorg:user:bar --limit=1
[
  "myorg:variable:foo/bar"
]
```

### Notes

For the flag `--role=<role>`, the description is as follows:

`Role to act as. By default, the current logged-in role is used. (default: none)`

On one hand we say that there is a default (the user currently logged-in) and then we say "(default: none)". This is countradictory and should be (default: logged-in user).

### Test plan

A full test plan will be provided in a separate document in this repo.

### Delivery plan

1. Implement additional functionality + UTs
   1. list --inspect *(2 days)*
   2. list --kind *(2 days)*
   3. list --search *(2 days)*
   4. list --limit *(2 days)*
   6. list --role=role *(2 days)*
   6. list --offset *(2 days)* -> low priority
3. Implement integration tests (*3 days*)
4. Ensure that existing UTs and integration tests are GA quality *(3 days)*
   1. Sit with QA to map out current tests and what is missing
   2. Implement missing tests (if required)
5. Write and get approval on UX logs from TW + PO *(2 days)*
6. Create documentation in `README.md` of the repository *(1 days)*
6. Write draft document for TW for online help and open a docs ticket for TW *(2 days)*

Total 23 days. Note this is not 23 days of consecutive work. There will be days of waiting for feedback and reviews.