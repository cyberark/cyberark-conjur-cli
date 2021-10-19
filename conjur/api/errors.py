# pylint: disable=line-too-long
class CertificateHostnameMismatchException(Exception):
    """ Exception for when machine's hostname does not match the hostname on the certificate """

    def __init__(self, message=""):
        super().__init__(message)


# pylint: disable=line-too-long
class InvalidParameterException(Exception):
    """ Exception for when machine's hostname does not match the hostname on the certificate """

    def __init__(self, message=""):
        super().__init__(message)
