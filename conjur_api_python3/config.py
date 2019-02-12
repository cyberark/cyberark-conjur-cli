import logging
import netrc
import os.path

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

NETRC_HOST_URL="{url}/authn"

class Config(object):
    DEFAULT_CONFIG_FILE = os.path.expanduser(os.path.join('~', '.conjurrc'))

    # We intentionally remap some fields to friendlier names
    FIELDS = [
        ('account', 'account'),
        ('appliance_url', 'url'),
        ('cert_file', 'ca_bundle'),
        ('plugins', 'plugins'),
    ]

    _config = {}

    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        logging.info("Trying to get configuration from filesystem ({})...".format(config_file))

        config = None
        with open(config_file, 'r') as config_fp:
            config = load(config_fp, Loader=Loader)

        for config_field_name, attribute_name in self.FIELDS:
            setattr(self, attribute_name, config[config_field_name])
            self._config[attribute_name] = getattr(self, attribute_name)

        logging.info("Trying to get API key from netrc...")
        netrc_obj = netrc.netrc()
        netrc_auth = netrc_obj.authenticators(NETRC_HOST_URL.format(**self._config))
        if netrc_auth is None:
            raise RuntimeError("Netrc didn't contain auth info for {}!".format(self._config['url']))

        login_id, _, api_key = netrc_auth

        setattr(self, 'api_key', api_key)
        setattr(self, 'login_id', login_id)

        self._config['api_key'] = api_key
        self._config['login_id'] = login_id

    def __repr__(self):
        return dump({'config': self._config}, Dumper=Dumper, indent=4)

    def __iter__(self):
       return iter(self._config.items())
