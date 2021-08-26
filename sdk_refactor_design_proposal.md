# SDK Refactor Design Proposal

#### Table of contents



### Motivation

During the push for GAing the CLI, it was realized that the SDK lacks the expandability and 



### Current SDK

#### Flow

![CurrentSDKFlow](/Users/Sigal.Sax/Downloads/CurrentSDKFlow.png)

At a high level, the SDK flow is as follows:

1. The user initializes the client, `client=conjur.Client(url="https://someserver", account="cucumber", password="123", ...)`
2. The *Client* constructor is then called, ensuring all configuration and credential information needed to make a request have been passed in. If not, it fetches the missing information in a discovery-like manner. For example, for `login`, if a Keystore is not available, it will attempt to fetch credentials from the .netrc.
3. *Client* is now initalized and the user can make a request, `list_values = client.list()`
4. The *Client* makes a call to *API* which handles the building of the request, merging paramters together, understanding what endpoint to use, etc.
5. The *API* makes a call to *HTTPWrapper* which escapes the parameters and invokes the endpoint to *ConjurAPI*.
6. Once the request is made and a response is returned, the *HTTPWrapper* hands back the information to the calling *API* which formats to the desired output.
7. *API* returns the formatted response to the *Client* and the *Client* returns it to the user. 

#### Limitations in current SDK Flow

The Client constructor resembles the following:

```python
# client.py
class Client():
    def __init__(self,
                 account: str = None,
                 api_key: str = None,
                 ca_bundle: str = None,
                 debug: bool = False,
                 http_debug=False,
                 login_id: str = None,
                 password: str = None,
                 ssl_verify: bool = True,
                 url: str = None):
      ...
      if not url or not login_id or (not password and not api_key):
        # load in Configuration details (if not provided)
        # load in Credential details (if not provided)
        # instantiate API objects according to the different params provided
        ...
        if api_key:
          ...
        elif password:
          ...
        else
          ...
       
```

See Client [code](https://github.com/cyberark/conjur-api-python3/blob/main/conjur/api/client.py#L51) for reference.

The Client class as a couple of limitations. The Client constructor is:

1. Not easily expandable. 

   a. The constructor's parameters in the method signature are not encapsulated. It accepts 9 hanging parameters when they can instead be encapsulated into related objects.

   b. The constructor expects to have all configuration and credentials loaded by the time it is instantiated. If not, it attempts to fetch the missing information. This is problematic for flows such as `init`,  `login` that have not yet been run and therefore cannot use the Client.

   c. In the CLI, we attempt to discover the organization's account for the user during the `init` flow. To get this information, we don't need to actually login to the Conjur server to get this information. We need to instead query `/info`. Because the Client is not expandable, this has forced us to bring over request logic to our logic code to avoid having to pass login information. See [InitLogic](https://github.com/cyberark/conjur-api-python3/blob/main/conjur/logic/login_logic.py#L54) for reference.

2. Implict instead of explicit. 

   a. As detailed above, the Client constuctor performs a sort of discovery depending on the paramter combination provided. A common example of this is when fetching credentials. The Client will search for credential details in the `.netrc` only if a Keystore is not found. This is unnecessarily added work and as a result of this implicity, the user needs to be fully aware of this environment instead of allowing him to choose.

3. Long and covers different domains.

   a. The constructor takes up 92 lines and handles fetching configuration and credential data, validating the input, configuring API calls, error handing, etc. This makes impacts code readability and should be broken up.

For these reasons, I propose we extract the configuration and credential information to their own classes to be created before the Client is called. In those classes, all the collection and validations will be performed. As a result, the Client constructor will not be forced to be incharge of handle multiple responsibilities.

We can handle the separation in one of the following ways:

|      | Solution                                        | Description                                                  | Pros                                                         | Cons                                                         |
| ---- | ----------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 1    | Keep as is                                      |                                                              | - Doesn't break current user apps<br />- Seems to be the direction the industry is going | - 92 lines and 9 params  so far making it unweidy<br />- Constructor is overloaded, handling multiple responsibilities<br />- Doesn't take advantage of OOP |
| 2    | Config/Creds objects for *each* supported flow  | ConfigurationFromFile()  - .conjurrc<br />ConfigurationFromEnv() - ENV vars<br />CredentialsFromFile() - netrc<br />CredentialsFromKeystore() - keystore | - Explicit, the flow the user chooses is very clear<br />- Security is up to user's the discretion | - Conflicting experience with CLI. The CLI performs a discovery on Config/Creds retrieval type |
| 3    | Generic Config/Creds object                     | Configuration()<br />Credentials()<br />and we will discover the flow based on environment's context | - Easy maintainability. No change in user's code as we build new ways to fetch config and creds<br />- Aligns with CLI UX of Config/Cred discovery | - Implicit and the user as they need to guess environment context |
| 4    | A single Config/Cred object with defining param | Configuration(file=true) - .conjurrc<br />Credential(keystore=true) | - Explicit<br />- Minimal code changes should the user choose a different flow<br />- Strong drive in Python to be as explicit as possible | - Requires changes in code if user wants to adopt another retrieval method<br />- Conflicting experience with CLI. The CLI preforms a discovery on Config/Creds retrieval type |

**Decision:** Option #4. 

The flow for configuration and credential will be determined explicitly by enabling the user to pass in the flow of their choosing via a parameter to the object during instantiation. 

This functionality will be implemented using the [Strategy pattern](https://refactoring.guru/design-patterns/strategy). Each Strategy will have its own implementation and validation mechanism. This will make the implementation easy to maintain as this makes it easy to swap algorithms used inside an object during runtime. That way, we can isolate the implementation details from the Client. If we choose to implement a new strategy, for example fetching values from ENV values, this will not require a change in any existing stategy.

Implementation:

```python
config = client.Configuration(file=True)
creds = client.Credental(keystore=True)
client. conjur.ConjurClient(config, creds, debug, ssl_verify)
```

We will still support the ability for users to build these objects themselves. If so, we won’t fetch the values from disk for them.

```python
config = client.Configuration(url="https://someserver", account="cucumber", cert_file="/some/certfile")
creds = client.Credental(machine="https://someserver", username="someuser", api_key="123")
client. conjur.ConjurClient(config, creds, debug, ssl_verify)
```



### Proposed SDK Flow

Configurations and credential retrieval



#### File structure

### Code

