import requests
import time
from ccdisplay import Display
from datetime import datetime
from exceptions import NoInternetException, FatalException, NonFatalFetchException
from imbox import Imbox
from userconfig import UserConfig
from ccutils import Switch, LightSensor, LED
import traceback

FETCH_DELAY_SECS = 60
NO_INTERNET_DELAY_SECS = 120


LIGHT_SENSOR_PIN = 5
SWITCH_PIN = 6
LED_PIN = 7
LIGHT_SENSOR_THRESHOLD = 120

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
        mail.mark_seen(m.message_id)
        if m.sent_from in cfg.emails and len(m.attachments):
            latest = m
            break
    return latest

def getContentFromAttachment(att) -> str:
    return att.get('content')

def displayMessage(msg: str):
    pass

def fetch(cfg: UserConfig, display: Display) -> None:
    if not connectedToInternet():
        raise NoInternetException
        
    mail = Imbox(cfg.imap_url, username=cfg.username, password=cfg.password,
                     ssl=True, ssl_context=None, starttls=False)

    msg = getLatestMessageWithAttachment(mail, cfg)
    if msg is None:
        log(f"No message found from whitelisted senders.")
        raise NonFatalFetchException
        
    new_text = getContentFromAttachment(msg)
    if new_text != display.text:
        display.updateText(new_text)

    log(f"Fetch successful. Waiting {FETCH_DELAY_SECS}s before fetching again.")

def run(cfg: UserConfig, display: Display):
    latest_fetch_time = 0
    sensor = LightSensor(LIGHT_SENSOR_PIN)
    switch = Switch(SWITCH_PIN)
    led = LED(LED_PIN)
    while True:
        try:
            if time.time() - latest_fetch_time >= FETCH_DELAY_SECS:
                fetch(cfg, display)
                latest_fetch_time = time.time()
        except NoInternetException:
            log(f"No Internet connection during fetch. Sleeping {NO_INTERNET_DELAY_SECS}s before cycling.")
            time.sleep(NO_INTERNET_DELAY_SECS)
        except NonFatalFetchException:
            log(f"Sleeping {FETCH_DELAY_SECS}s before cycling.")
            time.sleep(FETCH_DELAY_SECS)
        except Exception:
            log(f"Un unknown exception occurred: {traceback.print_exc()}. Cycling.")

        # Check if photosensor detects light (lid is open) or momentary switch is pressed (manual input)
        # RPi cannot read analog directly, so use ADC (analog to digital converter) chip like the MCP3008 https://www.adafruit.com/product/856
        if sensor.getLevel() >= LIGHT_SENSOR_THRESHOLD or switch.isPressed():
            display.on()
        else:
            display.off()
        

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