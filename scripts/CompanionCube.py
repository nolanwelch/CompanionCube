import os
import re
import requests
import time
import yaml
from datetime import datetime
from exceptions import InvalidConfigException, InvalidEmailException, NoKeysException, BadKeysException, NoConfigException, NoInternetException, FatalException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

RUN_DELAY_SECS = 60
NO_INTERNET_DELAY_SECS = 120

def log(msg: str):
    now = datetime.now()
    now = now.strftime('%m-%d-%Y %H:%M:%S')
    with open('../app.log', 'a+') as f:
        f.writelines([f'[{now}]   {msg}\n'])

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

def connectedToInternet() -> bool:
    r = requests.get('https://www.google.com')
    return bool(r.status_code)

def initialize():
    log("Beginning initialization.")
    if not connectedToInternet():
        log("No Internet connection at initialize()! Restarting device.")
        # TODO: Add log message
        raise NoInternetException
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

def run():
    while True:
        if not connectedToInternet():
            log(f"No Internet connection at top of run()! Sleeping {NO_INTERNET_DELAY_SECS}s.")
            time.sleep(NO_INTERNET_DELAY_SECS)
            continue

        log(f"End of run(). Sleeping {RUN_DELAY_SECS}s.")
        time.sleep(RUN_DELAY_SECS)

def main():
    try:
        initialize()
        run()
    except FatalException as e:
        log(f"Fatal exception: {repr(e)}")
        exit()

if __name__ == '__main__':
    main()