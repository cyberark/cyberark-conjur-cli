from enum import Enum


class ConjurEndpoint(Enum):
    AUTHENTICATE = "{url}/authn/{account}/{login}/authenticate"
    LOGIN = "{url}/authn/{account}/login"
    SECRETS = "{url}/secrets/{account}/{kind}/{identifier}"
