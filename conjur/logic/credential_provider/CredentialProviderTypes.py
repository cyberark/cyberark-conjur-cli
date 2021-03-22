from enum import Enum


class CredentialProviderTypes(Enum):
    NETRC = 1
    KEYSTORE = 2
    NONE = None
