# Nov12, 2022, ms
# mobileAway-simpler.py
'''
# MEMO: Nov12, 2022
simpler version
just to record phone-in, phone-out to toggl
raspi db is not used (no point, no bonus pint, no duration record)

desplay is re-designed as needed
'''

import board
import time
import toggltrack  # my
import adafruit_datetime
from digitalio import DigitalInOut, Direction, Pull
from adafruit_funhouse import FunHouse

from secrets import secrets  # my
import adafruit_requests
import wifi
import ssl
import socketpool


# -------------------------
# wifi internet connection
# -------------------------
print("Connecting to", secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to", secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# -----------------------
# funhouse initial setup
# -----------------------
funhouse = FunHouse(
    default_bg=0x0F0F00,
    scale=2,
)

# dotstar initial setting
funhouse.peripherals.set_dotstars(
    0x800080, 0x808000, 0x008000, 0x000080, 0x008080
)
funhouse.peripherals.dotstars.brightness = 0.1
time.sleep(1)
# dot star color lists
tiger_ptn = [0x635412, 0x000000, 0x635412, 0x000000, 0x635412]
all_red = [0x330000, 0x330000, 0x330000, 0x330000, 0x330000]
till_120 = [0x800080, 0x808000, 0x008000, 0x000080, 0x008080]
all_green = [0x003300, 0x003300, 0x003300, 0x003300, 0x003300]
all_yellow = [0x333300, 0x333300, 0x333300, 0x333300, 0x333300]
all_blue = [0x000033, 0x000033, 0x000033, 0x000033, 0x000033]
all_off = [0x000000, 0x000000, 0x000000, 0x000000, 0x000000]

# A2 ir break beam sensor
irbreak = DigitalInOut(board.A2)
irbreak.direction = Direction.INPUT
irbreak.pull = Pull.UP

# clear display
funhouse.display.show(None)

# labels
lb_time_away = funhouse.add_text(
    text="time away:", text_position=(3, 5), text_color=0x808080
)
lb_away_min3 = funhouse.add_text(
    text="", text_scale=4, text_position=(22, 32), text_color=0x808080
)
lb_away_min2 = funhouse.add_text(
    text="", text_scale=4, text_position=(37, 32), text_color=0x808080
)
lb_away_min1 = funhouse.add_text(
    text="", text_scale=4, text_position=(47, 32), text_color=0x808080
)
lb_min = funhouse.add_text(
    text="min", text_position=(96, 45), text_color=0x808080
)

lb_placed_removed = funhouse.add_text(
    text="", text_position=(3, 70), text_color=0x00AA66  # or 0xfaaf0c
)
lb_ymd = funhouse.add_text(
    text="", text_position=(8, 82), text_color=0xEEEEEE
)
lb_hms = funhouse.add_text(
    text="", text_position=(8, 94), text_color=0xEEEEEE
)

funhouse.display.show(funhouse.splash)


# ----------
# functions
# ----------
def controlDotstars(colors, on=True, last_only=False):
    if last_only:  # 'on/off' only the last, 'on' the rest
        for i in range(len(colors) - 1):
            funhouse.peripherals.dotstars[i] = colors[i]
        if on:
            funhouse.peripherals.dotstars[len(colors) - 1] = colors[-1]
        else:
            funhouse.peripherals.dotstars[len(colors) - 1] = 0x000000
    else:  # 'on/off' all
        for i in range(len(colors)):
            if on:
                funhouse.peripherals.dotstars[i] = colors[i]
            else:
                funhouse.peripherals.dotstars[i] = 0x000000


def showPlacedRemoved(is_in, timestamp):
    '''
    show placed, removed since... and time stamp
    '''
    ymd, hms = timestamp.split('T')

    if is_in:  # placed
        funhouse.set_text("Mobile is Away!", lb_placed_removed)
        funhouse.set_text_color(0x11faa9, lb_placed_removed)
        funhouse.set_text(ymd, lb_ymd)
        funhouse.set_text(hms, lb_hms)
    else:
        funhouse.set_text("Removed...", lb_placed_removed)
        funhouse.set_text_color(0xfaaf0c, lb_placed_removed)
        funhouse.set_text(ymd, lb_ymd)
        funhouse.set_text(hms, lb_hms)


def showDuration(num, color):
    """
    control text_color and text position based on the digits
    set_text_color method is available, but there is no
    set_text_position...
    so 3 labels are prepared and select one of them with digits of the number.
    non use labels are invisible with blank text
    """
    labels = [lb_away_min1, lb_away_min2, lb_away_min3]

    # determine digits to use
    if num == -1:
        digits = 2
    elif num < 10:
        digits = 1
    elif num < 100:
        digits = 2
    else:
        digits = 3

    for i, label in enumerate(labels):
        if digits == i + 1:
            if num == -1:
                num = '--'
            funhouse.set_text(num, label)
            funhouse.set_text_color(color, label)
        else:
            funhouse.set_text("", label)


def getColorParameters(duration):
    """
    returns
    ptn->list: dotstar pattern. how many to use and their colors
    last_only->bool: last dotstar control. blink or ever on
    fcol->hex color: color for duration display font.
                    Colors are adjusted to match dotstar color.
    # Nov 12, 2022
    duration = -1 means phone is not placed
    """
    last_only = True
    if duration == -1:
        ptn = tiger_ptn
        fcol = 0xfaaf0c
        last_only = False
    elif duration < 15:
        ptn = till_120[:1]
        fcol = 0xEE00EE
    elif duration < 30:
        ptn = till_120[:2]
        fcol = 0xEEEE00
    elif duration < 60:
        ptn = till_120[:3]
        fcol = 0x00EE00
    elif duration < 90:
        ptn = till_120[:4]
        fcol = 0x8a99ff
    elif duration < 120:
        ptn = till_120
        fcol = 0x00EEEE
    else:
        ptn = till_120
        fcol = 0x00EEEE
        last_only = False
    return ptn, fcol, last_only


def buzz(freq, tone_duration, wait, repeat, hahaha=False):
    for i in range(repeat):
        funhouse.peripherals.play_tone(freq, tone_duration)
        time.sleep(wait)
    if hahaha:
        buzz(freq, tone_duration/2, wait/2, repeat)
        # buzz(freq, tone_duration/4, wait/4, repeat)
        # buzz(freq, tone_duration/6, wait/6, repeat*2)
        # buzz(freq, tone_duration/8, wait/8, repeat*2)
        # buzz(freq, tone_duration/10, wait/10, repeat*2)
        # buzz(freq*2, tone_duration/10, wait/10, repeat*2)
        # buzz(freq*6, tone_duration/10, wait/10, repeat*2)
        # buzz(freq*10, tone_duration/10, wait/10, repeat*5)
        buzz(freq, 1, 1, 3)


def utcISO2localTS(utc_iso):
    utc_dt_obj = adafruit_datetime.datetime.fromisoformat(utc_iso)
    offset = adafruit_datetime.timedelta(hours=8)  # UTC+8
    local_dt_obj = utc_dt_obj + offset
    local_iso = local_dt_obj.isoformat()
    return local_iso
    #return local_dt_obj.strftime('%d%b%Y-%H%M%S')  # strftime not implemented


# ------------------------------
# loop variables initialization
# ------------------------------
was_in = False  # previous placed/removed status
dotstar_on = True  # dotstar blinking control
prev = 0  # to count ~ 1 second
# to count up 'away' duration
delta = 0
duration = -1

entry_id = None
dotstar_ptn = till_120

# -----
# loop
# -----
while True:
    now = time.monotonic()

    # update sensor status
    is_in = not irbreak.value

    # when phone is placed or removed
    if is_in != was_in:
        # off dotstars
        controlDotstars(all_off, on=False, last_only=False)
        # update last status
        was_in = is_in
        # placed-removed branching
        if is_in:  # ===== PHONE PLACED ======================================
            # 1. start toggl
            entry_id, utc_start_iso = toggltrack.startTimeEntry(
                        requests, "Away from my phone.",
                        secrets['away-from-phone-pid'],
                        secrets['G1-wid'], secrets['authB-G1']
                        )

            # 2. #TODO: update display
            start_timestamp = utcISO2localTS(utc_start_iso)
            print('[debug] start_timestamp:', start_timestamp)
            showPlacedRemoved(is_in, start_timestamp)
            # 3. buzzer (good)
            buzz(880, 0.4, 0.2, 2)
            # 4. initialize count up vars
            delta, duration = 0, 0
        else:  # ===== PHONE REMOVED =========================================
            # 1. stop toggl
            if entry_id is not None:
                utc_stop_iso = toggltrack.stopTimeEntry(
                    requests, entry_id, secrets['authB-G1']
                    )
                entry_id= None
            # 2. # TODO: update display
            stop_timestamp = utcISO2localTS(utc_stop_iso)
            print('[debug] stop_timestamp:', stop_timestamp)
            showPlacedRemoved(is_in, stop_timestamp)
            # 3. buzzer (bad)
            buzz(330, 0.1, 0.05, 30, True)
        # update prev
        prev = now
        continue

    # ===== 1 second trap =====
    if now - prev > 1:
        # dotstar blinking
        dotstar_on = not dotstar_on
        if is_in:  # ===== PHONE IS IN =======================================
            delta += now - prev  # second
            duration = int(delta // 60)  # min
        else:  # ===== PHONE IS NOT IN =======================================
            duration = -1  # phone is not in

        # to control dotstar
        ptn, font_col, last_only = getColorParameters(duration)
        controlDotstars(ptn, dotstar_on, last_only=last_only)
        # update display
        showDuration(num=duration, color=font_col)

        # update prev
        prev = now
        # continue
