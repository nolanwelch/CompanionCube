import os
import re
import requests
import time
import yaml
from ccdisplay import Display
from datetime import datetime
from exceptions import InvalidConfigException, InvalidEmailException, NoKeysException, BadKeysException, NoConfigException, NoInternetException, FatalException
from imbox import Imbox
from userconfig import UserConfig
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

def connectedToInternet() -> bool:
    r = requests.get('https://www.google.com')
    return bool(r.status_code)

def loadConfig() -> UserConfig:
    log("Loading config.")
    if not connectedToInternet():
        log("No Internet connection at loadConfig()")
        raise NoInternetException
    cfg = UserConfig('../config/config.yaml')
    return cfg

def loadDisplay() -> Display:
    pass

def getLatestMessageWithAttachment(mail: Imbox, cfg: UserConfig):
    messages = mail.messages(unread=True)
    latest = None
    for m in messages:
        if m.sent_from in cfg.emails and len(m.attachments):
            latest = m
            break
    return latest

def getContentFromAttachment(att) -> str:
    return att.get('content')

def displayMessage(msg: str):
    pass

def run(cfg: UserConfig, display: Display):
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
            new_text = getContentFromAttachment(msg)
            if new_text != display.text:
                display.updateText(new_text)
        except:
            log(f"Un unknown exception occurred: {traceback.print_exc()}. Cycling.")
            continue
        
        


        log(f"End of run(). Sleeping {RUN_DELAY_SECS}s before cycling.")
        time.sleep(RUN_DELAY_SECS)

def main():
    try:
        cfg: UserConfig = loadConfig()
        display: Display = loadDisplay()
        log("Config successfully loaded.")
        run(cfg, display)
    except FatalException as e:
        log(f"Fatal exception: {repr(e)}. Restarting device.")
        exit()

if __name__ == '__main__':
    main()