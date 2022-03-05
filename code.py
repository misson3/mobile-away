# ========================================================== this is for GitHub
# Feb14, 19, 20, 26, 27, 28, Mar01, 04, 05, 2022, ms
# code for mobile-away (k-tai-away)
# code.py

import board
import time
import toggltrack  # my
import dbAccess  # my
import adafruit_datetime
from digitalio import DigitalInOut, Direction, Pull
from adafruit_funhouse import FunHouse

from secrets import secrets
import adafruit_requests
import wifi
import ssl
import socketpool

import random

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
all_red = [0x330000, 0x330000, 0x330000, 0x330000, 0x330000]
till_120 = [0x800080, 0x808000, 0x008000, 0x000080, 0x008080]
all_green = [0x003300, 0x003300, 0x003300, 0x003300, 0x003300]
all_yellow = [0x333300, 0x333300, 0x333300, 0x333300, 0x333300]
all_blue = [0x000033, 0x000033, 0x000033, 0x000033, 0x000033]

mode2col_no_phone = {0: all_green, 1: all_yellow, 2: all_red}

# A2 ir break beam sensor
irbreak = DigitalInOut(board.A2)
irbreak.direction = Direction.INPUT
irbreak.pull = Pull.UP

# fixed labels
funhouse.display.show(None)
flb_points = funhouse.add_text(
    text="Points:", text_position=(3, 70), text_color=0xAAAA00
)
flb_bonus = funhouse.add_text(
    text=" Bonus:", text_position=(3, 82), text_color=0xAAAA00
)
flb_total = funhouse.add_text(
    text=" Today:", text_position=(3, 94), text_color=0xAAAA00
)
flb_min_today = funhouse.add_text(
    text="min", text_position=(100, 94), text_color=0x808080
)
flb_min_month = funhouse.add_text(
    text="min", text_position=(100, 110), text_color=0x808080
)
flb_month = funhouse.add_text(
    text="Month:", text_position=(3, 110), text_color=0xCCCC00
)

# variable labels
lb_time_away = funhouse.add_text(
    text="", text_position=(3, 5), text_color=0x808080
)
lb_waiting = funhouse.add_text(
    text="WAITING...", text_position=(35, 30), text_color=0x00EE00
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
    text="", text_position=(96, 45), text_color=0x808080
)
lb_points = funhouse.add_text(
    text="0", text_position=(48, 70), text_color=0xEEEEEE
)
lb_bonus = funhouse.add_text(
    text="0", text_position=(48, 82), text_color=0xEEEEEE
)
lb_today = funhouse.add_text(
    text="0", text_position=(48, 94), text_color=0xEEEEEE
)
lb_dur_today = funhouse.add_text(
    text='{:>3}'.format(0), text_position=(80, 94), text_color=0x00AA66
)
lb_month = funhouse.add_text(
    text="0", text_position=(42, 110), text_color=0xEEEEEE
)
lb_dur_this_mon = funhouse.add_text(
    text='{:>4}'.format(0), text_position=(74, 110), text_color=0x00AA66
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


def blinkLabel(label_name, mode, blinker):
    mode2txt = {0: 'WAITING...',
                1: 'BED TIME!',
                2: 'VIOLATION!'}
    mode2txt_col = {0: 0x00EE00,
                    1: 0xEEEE00,
                    2: 0xEE0000}
    # blank lb_away_min3
    funhouse.set_text("", lb_away_min3)
    if blinker:
        funhouse.set_text(mode2txt[mode], label_name)
        funhouse.set_text_color(mode2txt_col[mode], label_name)
    else:
        funhouse.set_text("", label_name)


def switchDisplayMode(mode):
    '''
    hide show labels for different modes
    '''
    if mode == 'waiting':
        funhouse.set_text("", lb_time_away)
        funhouse.set_text("", lb_min)
        funhouse.set_text("", lb_away_min1)
        funhouse.set_text("", lb_away_min2)
        funhouse.set_text("", lb_away_min3)
        funhouse.set_text("WAITING...", lb_waiting)
    elif mode == 'counting':
        funhouse.set_text("time away:", lb_time_away)
        funhouse.set_text("min", lb_min)
        funhouse.set_text("", lb_waiting)
    elif mode == 'bedtime':
        funhouse.set_text("", lb_time_away)
        funhouse.set_text("", lb_min)
        funhouse.set_text("", lb_away_min1)
        funhouse.set_text("", lb_away_min2)
        funhouse.set_text("Zzz...", lb_away_min3)
        funhouse.set_text_color(0x00AAEE, lb_away_min3)
        funhouse.set_text("", lb_waiting)


def showDuration(num, color):
    """
    control text_color and text position based on the digits
    set_text_color method is available, but there is no
    set_text_position...
    so 3 labels are prepared and select one of them with digits of the number.
    non use labels are invisible with blank text
    """
    labels = [lb_away_min1, lb_away_min2, lb_away_min3]
    if num < 10:
        digits = 1
    elif num < 100:
        digits = 2
    else:
        digits = 3

    for i in range(3):
        if digits == i + 1:
            funhouse.set_text(num, labels[i])
            funhouse.set_text_color(color, labels[i])
        else:
            funhouse.set_text("", labels[i])


def getColorParameters(duration):
    """
    returns
    ptn->list: dotstar pattern. how many to use and their colors
    last_only->bool: last dotstar control. blink or ever on
    col->hex color: duration display color.
                    Colors are adjusted to match dotstar color.
    """
    last_only = True
    if duration < 15:
        ptn = till_120[:1]
        col = 0xEE00EE
    elif duration < 30:
        ptn = till_120[:2]
        col = 0xEEEE00
    elif duration < 60:
        ptn = till_120[:3]
        col = 0x00EE00
    elif duration < 90:
        ptn = till_120[:4]
        col = 0x8a99ff
    elif duration < 120:
        ptn = till_120
        col = 0x00EEEE
    else:
        ptn = till_120
        col = 0x00EEEE
        last_only = False
    return ptn, col, last_only


def durationToPoints(duration):
    """
    less than 15 is not considered 'away'.
    """
    if duration < 15:
        points = 0
    else:
        points = duration
    return points


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


def getCurrentTime():
    aio_username = secrets["aio_username"]
    aio_key = secrets["aio_key"]
    location = secrets.get("timezone", None)
    TIME_URL = "https://io.adafruit.com/api/v2/%s/integrations/time/strftime?x-aio-key=%s" % (aio_username, aio_key)
    TIME_URL += "&fmt=%25Y-%25m-%25d+%25H%3A%25M%3A%25S.%25L+%25j+%25u+%25z+%25Z"
    response = requests.get(TIME_URL)
    # print(response.text)  # 2022-02-26 10:32:23.340 057 6 +0800 +08
    # set initial local time
    iso_string = 'T'.join(response.text.split(' ')[0:2])
    local_time = adafruit_datetime.datetime.fromisoformat(iso_string)
    return local_time


def checkAndSwitchMode(local_time, current_mode):
    print('[debug] checkAndSwitchMode():', local_time)
    # key time points
    tp_6am = (6, 0)  # 6h 0m
    tp_10pm = (22, 0)  # 22h 0m
    tp_0am = (0, 0)  # 0h 0m

    h = local_time.hour
    m = local_time.minute

    new_mode = current_mode
    if (h, m) == tp_6am:
        new_mode = 0
    elif (h, m) == tp_10pm:
        new_mode = 1
    elif (h, m) == tp_0am:
        new_mode = 2

    changed = False
    if current_mode != new_mode:
        changed = True
        print('[debug] mode changed:', current_mode, '->', new_mode)
    else:
        print('[debug] mode:', current_mode)
    print()

    return new_mode, changed


def adjustBeforeKeyTimePoints(local_time, *hs):
    """
    check if local_time is 5 min be fore h in hs
    if so, get current time from internet and set it to local_time
    Use 24 for 0am
    """
    print('[debug] adjustBeforeKeyTimePoints():', local_time)
    # if it does not hit, no addjustment is done
    lc_h = local_time.hour
    lc_m = local_time.minute
    adjusted = False
    for h in hs:
        if (lc_h, lc_m) == (h - 1, 55):
            local_time = getCurrentTime()
            adjusted = True
            print('[debug] time adjusted:', local_time)
            break
        else:
            pass
            # print('[debug]', (lc_h, lc_m), 'is not', (h, 55))

    return local_time, adjusted


def checkBonus(duration):
    """
    note: bonux_box dict is outside
    """
    bonus_to_add = 0
    if duration in bonus_box:
        bonus_to_add = bonus_box[duration]
        bonus_box[duration] = 0  # you can get only once per duration

    return bonus_to_add


def startToggl(requests):
    entry_id = toggltrack.startTimeEntry(
                requests, "Away from my phone.",
                secrets['away-from-phone-pid'],
                secrets['G1-wid'], secrets['authB-G1']
                )
    return entry_id


# for start of the day (including system restart)
def getPBDSumsFromDB(select_by, requests):
    pbds = dbAccess.getDataByFrom3B1(select_by, requests)
    # pbds is list of [points, bonus, duration] from selection
    # tuple becomes list via packing into json (see raspi side code)
    # take sums
    points = sum([lis[0] for lis in pbds])
    bonus = sum([lis[1] for lis in pbds])
    duration = sum([lis[2] for lis in pbds])

    pbd_sums = (points, bonus, duration)

    return pbd_sums


def updateCounterLabels(points, bonus, p_today, dur_today,
                        p_mon, dur_this_mon):
    """
    update 6 counter labels
    """
    funhouse.set_text(points, lb_points)
    funhouse.set_text(bonus, lb_bonus)
    funhouse.set_text(p_today, lb_today)
    funhouse.set_text('{:>3}'.format(dur_today), lb_dur_today)
    funhouse.set_text(p_mon, lb_month)
    funhouse.set_text('{:>4}'.format(dur_this_mon), lb_dur_this_mon)


def sendMsgTo3B1(msg, lang, requests):
    """
    ask google home to announce
    node-red is working on 3Bp1
    """
    host = secrets['raspi_announcement']
    # lang = 'en-US'  # only ja for now.
    myData = {'message': msg, 'language': lang}
    print('[debug sendMsgTo3B1()] posting:', msg)
    res = requests.post(host, data=myData)
    print('[debug sendMsgTo3B1()] response:', res)

    return 'sending message done!'


# ------------------------------
# loop variables initialization
# ------------------------------
was_in = False
prev = 0  # to count ~ 1 second
prev_60 = 0  # to count ~ 60 seconds
prev_300 = 0  # to count ~ 300 seconds
delta = 0
duration = 0
blinker = True
bonus_box = {30: 5, 60: 15, 90: 25, 120: 35}
# get current time from internet
local_time = getCurrentTime()
print('[debug] current time from internet:', local_time)
mode, changed = checkAndSwitchMode(local_time, 0)
print('[debug] startup mode is:', mode)
prev_mode = 0


# ---------------------------------------------------
# setting vars from historical data from db (on 3B1)
# ---------------------------------------------------
'''
1. get followings from Maria DB
select_by = 'today'
    points, bonus, today, dur_today
select_by = 'this_month'
    p_mon, dur_this_mon
2. update corresponding labels
'''
points, bonus, dur_today = getPBDSumsFromDB('today', requests)
p_today = points + bonus
# reset points and bonus before the loop starts
points, bonus = 0, 0

_points, _bonus, dur_this_mon = getPBDSumsFromDB('this_month', requests)
p_mon = _points + _bonus

updateCounterLabels(points, bonus, p_today, dur_today, p_mon, dur_this_mon)

# ---------------
# alert messages
# ---------------
msges = [
    ("Message sentence 1", "en-US"),
    ("Message sentence 2.", "en-US"),
    ("日本語のメッセージ", "ja")
]


# -----
# loop
# -----
while True:
    now = time.monotonic()

    # sensor status
    is_in = not irbreak.value

    # when status change occurred
    if is_in != was_in:
        was_in = is_in  # update last status
        if is_in:  # phone was put
            if mode == 0:
                controlDotstars(all_red, on=False)  # off all.
                switchDisplayMode('counting')
                # reset bonus box!
                bonus_box = {30: 5, 60: 10, 90: 10, 120: 10}
                entry_id = startToggl(requests)
            prev = now
            buzz(880, 0.4, 0.2, 2)
        else:  # phone was removed
            if mode == 0:
                switchDisplayMode('waiting')
                # calculate this duration result
                p_today += points + bonus
                p_mon += points + bonus
                dur_today += duration
                dur_this_mon += duration
                # end toggl
                toggltrack.stopTimeEntry(requests, entry_id,
                                         secrets['authB-G1'])
                # send points, bonus, duration to MariaDB on 3B1
                dbAccess.postTimeEntryTo3B1(points, bonus, duration, requests)
                # reset points, bonus, duration
                points, bonus, delta, duration = 0, 0, 0, 0
                # reset, update counter labels
                updateCounterLabels(
                    points, bonus, p_today, dur_today, p_mon, dur_this_mon
                )
                buzz(330, 0.1, 0.05, 30, True)
            elif mode == 1.5:
                # first removal after 6am
                print('GOOD MORNING!')
                switchDisplayMode('waiting')
                buzz(880, 0.2, 0.2, 5)
                mode = 0
            elif mode in (1, 2):
                buzz(330, 0.1, 0.05, 30, True)
        continue

    # ===== 1 second trap =====
    if now - prev > 1:
        blinker = not blinker  # flip bool
        # when phone is in
        if is_in and mode == 0:
            delta += now - prev  # second
            duration = int(delta // 60)  # min
            # to control dotstar
            ptn, col, last_only = getColorParameters(duration)
            controlDotstars(ptn, blinker, last_only=last_only)
            # update display
            showDuration(num=duration, color=col)
            points = durationToPoints(duration)
            bonus += checkBonus(duration)
            funhouse.set_text(points, lb_points)
            funhouse.set_text(bonus, lb_bonus)
        elif is_in and mode in (1, 2, 1.5):  # mode=1.5 added -----
            controlDotstars(all_blue, True)
            switchDisplayMode('bedtime')
        # when phone is NOT in
        else:
            # blink all dotstars and msg
            controlDotstars(mode2col_no_phone[mode], blinker)
            blinkLabel(lb_waiting, mode, blinker)
        prev = now

    # ===== 60 second trap =====
    if now - prev_60 > 60:
        # increment local time by 60 seconds
        local_time = local_time + adafruit_datetime.timedelta(seconds=60)
        # time adjustment if it is 5 min before key time points
        # TUNE: 6, 22, 24 are the key time points
        # TUNE: i added more for testing
        local_time, adjusted = adjustBeforeKeyTimePoints(
                                local_time, 6, 13, 14, 15, 16, 27, 18, 19, 20,
                                21, 22, 23, 24)
        # mode switching if it hits key time points
        mode, changed = checkAndSwitchMode(local_time, mode)  # changed -> bool

        if changed:
            # MEMO: when mode changed from 2 to 0 -> a new day started!
            if (prev_mode, mode) == (2, 0):
                # init vars for today
                points, bonus, dur_today = getPBDSumsFromDB('today', requests)
                p_today = points + bonus
                _points, _bonus, dur_this_mon = getPBDSumsFromDB(
                                                    'this_month',
                                                    requests
                                                )
                p_mon = _points + _bonus
                updateCounterLabels(
                    points, bonus, p_today, dur_today, p_mon, dur_this_mon
                )
                # IDEA: set mode=1.5 until phone is removed.
                mode = 1.5
            # MEMO: when mode changed from 0 to 1 -> end of the day
            elif (prev_mode, mode) == (0, 1):
                if is_in:
                    # calculate this duration result
                    p_today += points + bonus
                    p_mon += points + bonus
                    dur_today += duration
                    dur_this_mon += duration
                    # end toggl
                    toggltrack.stopTimeEntry(
                        requests, entry_id, secrets['authB-G1']
                    )
                    # send points, bonus, duration to MariaDB on 3B1
                    dbAccess.postTimeEntryTo3B1(
                        points, bonus, duration, requests
                    )
                    # update counter labels
                    updateCounterLabels(
                        points, bonus, p_today, dur_today, p_mon, dur_this_mon
                    )
                # common tasks
                buzz(880, 0.2, 0.2, 5)
                switchDisplayMode('bedtime')
            prev_mode = mode

        # test
        # mode = 2

        prev_60 = now
        if adjusted:
            sec_to_slide = local_time.second
            prev_60 -= sec_to_slide

    # ===== 300 second trap =====
    if now - prev_300 > 300:
        # announce in every 5 min until phone is placed
        if (mode == 1) and (not is_in):
            # msg to google home via NodeRed on 3B1
            msg, lang = msges[random.randint(0, len(msges)-1)]
            done = sendMsgTo3B1(msg, lang, requests)
            print(done)
            print()
        prev_300 = now
