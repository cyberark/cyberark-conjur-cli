# Note this file should move to conjur project
from conjur.constants import *


class ConfigFile:
    def __init__(self, account=None, conjur_url=None, cert_file=None):
        self.account = account
        self.conjur_url = conjur_url
        self.cert_file = cert_file

    def __str__(self):
        str = "---\n"
        str += f"conjur_account: {self.account}\n"
        str += f"conjur_url: {self.conjur_url}\n"
        str += f"cert_file: {self.cert_file}\n"
        return str

    def dump_to_file(self, file_path=DEFAULT_CONFIG_FILE):
        with open(file_path, 'w') as f:
            f.write(self.__str__())

    @staticmethod
    def from_file(file_path=DEFAULT_CONFIG_FILE):
        # note this function parse file with only one configuration in it
        ret = ConfigFile()
        with open(file_path, 'r') as f:
            for line in f.readlines():
                if line.strip().startswith('conjur_account'):
                    ret.account = "".join(line.split(":")[1:]).strip()
                if line.strip().startswith('conjur_url'):
                    ret.conjur_url = "".join(line.split(":")[1:]).strip()
                if line.strip().startswith('cert_file'):
                    ret.cert_file = "".join(line.split(":")[1:]).strip()
