import requests
import time
from ccdisplay import Display
from datetime import datetime
from exceptions import NoInternetException, FatalException, NonFatalFetchException
from imbox import Imbox
from ccuserconfig import UserConfig
from ccutils import Switch, LightSensor, LED
from traceback import print_exc

FETCH_DELAY_SECS = 60
NO_INTERNET_DELAY_SECS = 120

LIGHT_SENSOR_PIN = 5
SWITCH_PIN = 6
LED_PIN = 7
LIGHT_SENSOR_THRESHOLD = 120

DEBUG_SWITCH_PRESS_SECS = 5

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
    display = Display(None)
    return display

def getLatestMessageWithAttachment(mail: Imbox, emails: list[str]):
    messages = mail.messages(unread=True)
    latest = None
    for m in messages:
        mail.mark_seen(m.message_id)
        if m.sent_from in emails and len(m.attachments):
            latest = m
            break
    return latest

def getContentFromAttachment(att) -> str:
    return att.get('content')

def fetch(cfg: UserConfig) -> str:
    if not connectedToInternet():
        raise NoInternetException
        
    mail = Imbox(cfg.imap_url, username=cfg.username, password=cfg.password,
                     ssl=True, ssl_context=None, starttls=False)

    msg = getLatestMessageWithAttachment(mail, cfg.emails)
    if msg is None:
        log(f"No message found from whitelisted senders.")
        raise NonFatalFetchException
        
    fetched_content = getContentFromAttachment(msg)

    log(f"Fetch successful. Waiting {FETCH_DELAY_SECS}s before fetching again.")
    return fetched_content

def run(cfg: UserConfig, display: Display):
    debug_mode = False

    latest_fetch_time = 0
    cycle_sleep_secs = 0
    sleep_start_time = 0
    switch_press_start_time = 0
    light_sensor = LightSensor(LIGHT_SENSOR_PIN)
    switch = Switch(SWITCH_PIN)
    led = LED(LED_PIN)
    while True:
        # program-assigned sleep timer
        if time.time() - sleep_start_time >= cycle_sleep_secs:
            try:
                if time.time() - latest_fetch_time >= FETCH_DELAY_SECS:
                    fetched_msg = fetch(cfg)
                    latest_fetch_time = time.time()
                    display.updateText(fetched_msg)
            except NoInternetException:
                log(f"No Internet connection during fetch. Sleeping {NO_INTERNET_DELAY_SECS}s before cycling.")
                display.updateText("No Internet connection.")
                cycle_sleep_secs = NO_INTERNET_DELAY_SECS
            except NonFatalFetchException:
                log(f"Sleeping {FETCH_DELAY_SECS}s before cycling.")
                cycle_sleep_secs = FETCH_DELAY_SECS
            except Exception:
                log(f"Un unknown exception occurred: {print_exc()}. Cycling.")
        
        # debug mode switch press timer
        if switch.isPressed():
            if switch_press_start_time == 0:
                switch_press_start_time = time.time()
            elif time.time() - switch_press_start_time >= DEBUG_SWITCH_PRESS_SECS:
                debug_mode = True
                display.updateText("DEBUG MODE")
        else:
            switch_press_start_time = 0

        # Check if photosensor detects light (lid is open) or momentary switch is pressed (manual input)
        # RPi cannot read analog directly, so use ADC (analog to digital converter) chip like the MCP3008 https://www.adafruit.com/product/856
        if light_sensor.getLevel() >= LIGHT_SENSOR_THRESHOLD or switch.isPressed():
            led.disable()
            display.on()
        else:
            led.enable()
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