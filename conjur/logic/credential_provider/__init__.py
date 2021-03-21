"""
credential_provider

This package contains the logic for credential providers
"""

from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.logic.credential_provider.keystore_credentials_provider \
    import KeystoreCredentialsProvider
from conjur.logic.credential_provider.credential_store_factory import CredentialStoreFactory
