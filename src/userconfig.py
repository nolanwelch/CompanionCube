import os
import re
import yaml
from exceptions import NoConfigException, InvalidConfigException, InvalidEmailException

class UserConfig:
    def __init__(self, path: str):
        self.path = path
        self.emails = []
        if not os.path.exists(path):
            raise NoConfigException
        with open(path, 'r') as f:
            cfg = yaml.safe_load(f)
            if set(['whitelist', 'username', 'password', 'imap-url']) != set(cfg.keys()):
                raise InvalidConfigException
            cfg['whitelist'] = cfg['whitelist'].split(' ')
            for email in cfg['whitelist']:
                if type(email) is str and self.__is_email(email):
                    self.emails.append(email)
                else:
                    raise InvalidEmailException(email)
            if type(cfg['username']) is str and self.__is_email(cfg['username']):
                self.username = cfg['username']
            else:
                raise InvalidEmailException
            if type(cfg['password']) is str:
                self.password = cfg['password']
            else:
                raise InvalidConfigException
            if type(cfg['imap-url']) is str:
                self.imap_url = cfg['imap-url']
            else:
                raise InvalidConfigException

    def __is_email(self, s: str):
        return re.match(r"^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", s) != None
