import os
import re
import requests
import time
import yaml
from datetime import datetime
from exceptions import InvalidConfigException, InvalidEmailException, NoKeysException, BadKeysException, NoConfigException, NoInternetException, FatalException
from imbox import Imbox
import traceback

RUN_DELAY_SECS = 60
NO_INTERNET_DELAY_SECS = 120

def log(msg: str):
    now = datetime.now()
    now = now.strftime('%m-%d-%Y %H:%M:%S')
    out_str = f'[{now}]   {msg}'
    with open('../app.log', 'a+') as f:
        f.write(f'{out_str}\n')
    print(out_str)

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

def loadConfig():
    log("Loading config.")
    if not connectedToInternet():
        log("No Internet connection at loadConfig()")
        raise NoInternetException
    cfg = Config('../config/config.yaml')
    return cfg
        
def getLatestMessageWithAttachment(mail: Imbox, cfg: Config):
    messages = mail.messages(unread=True)
    latest = None
    for m in messages:
        if m.sent_from in cfg.emails and len(m.attachments):
            latest = m
            break
    return latest

def downloadAttachment(msg) -> None:
    attachment = msg.attachments[0]
    att = attachment.get('filename')
    download_path = f"../temp/{att}"
    with open(download_path, 'wb') as f:
        f.write(attachment.get('content').read())

def run(cfg: Config):
    mail = None
    while True:
        log("Starting run() cycle.")
        
        if mail is not None:
            log("Reset mail object and logged out.")
            mail.logout()
            mail = None
        
        if not connectedToInternet():
            log(f"No Internet connection at top of run(). Sleeping {NO_INTERNET_DELAY_SECS}s before cycling.")
            time.sleep(NO_INTERNET_DELAY_SECS)
            continue
        
        mail = Imbox(cfg.imap_url, username=cfg.username, password=cfg.password,
                     ssl=True, ssl_context=None, starttls=False)

        msg = getLatestMessageWithAttachment(mail, cfg)
        if msg is None:
            log(f"No message found from whitelisted senders.")
            log(f"Sleeping {RUN_DELAY_SECS}s before cycling.")
            time.sleep(RUN_DELAY_SECS)
            continue
        
        try:
            downloadAttachment(msg)
        except:
            log(f"Un unknown exception occurred: {traceback.print_exc()}. Cycling.")
            continue



        log(f"End of run(). Sleeping {RUN_DELAY_SECS}s before cycling.")
        time.sleep(RUN_DELAY_SECS)

def main():
    try:
        cfg: Config = loadConfig()
        log("Config successfully loaded.")
        run(cfg)
    except FatalException as e:
        log(f"Fatal exception: {repr(e)}. Restarting device.")
        exit()

if __name__ == '__main__':
    main()