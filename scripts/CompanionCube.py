import logging
import os.path
import re
import yaml
from exceptions import InvalidConfigException, InvalidEmailException, NoKeysException, BadKeysException, NoConfigException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def log(msg: str):
    logging.warning(msg)

class Config:
    def __init__(self, path: str):
        self.path = path
        self.emails = []
        if not os.path.exists(path):
            raise NoConfigException
        with open(path, 'r') as f:
            cfg = yaml.safe_load(f)
            if set(['whitelist', 'username', 'password', 'imap-url']) != set(cfg.keys()):
                raise InvalidConfigException
            for email in cfg['whitelist']:
                if type(email) is str and self.__is_email(email):
                    self.emails.append(email)
                else:
                    raise InvalidEmailException
            if type(cfg['username']) is str and self.__is_email(cfg['username']):
                self.username = cfg['username']
            else:
                raise InvalidEmailException
            if type(cfg['password']) is str:
                self.password = cfg['password']
            else:
                raise InvalidConfigException
            if type(cfg['imap-url']) is str and re.match(r"""/^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.
                                                         [a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$/""",
                                                         cfg['imap-url']):
                self.imap_url = cfg['imap-url']
            else:
                raise InvalidConfigException

    def __is_email(self, s: str):
        return re.match(r"^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$", s)
                

def start():
    cfg = Config('../config/config.yaml')
    creds = None
    if os.path.exists('../config/keys.json'):
        creds = Credentials.from_authorized_user_file('../config/keys.json',
                                                      ['https://www.googleapis.com/auth/gmail.readonly'])
    else:
        raise NoKeysException
    if not creds.valid:
        raise BadKeysException
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels(userId='me').execute()
        labels = results.get('labels', [])

    except:
        # TODO: Add error handling for improper API startup
        pass 

def main():
    logging.basicConfig(filename='../app.log', filemode='w', format='%(asctime)s - %(message)s',
                        datefmt='%m-%d-%Y %H:%M:%S')
    log('test')
    # TODO: Get logging system working
    quit()
    start()


if __name__ == '__main__':
    main()