# ========================================================== this is for GitHub
# Feb20, 2022, ms
# dbAccess.py
# functions to access Mariadb on 3B1

# create following json and send it to flask server on 3B1
# {'points': INT, 'bonus': INT, 'duration': INT}
# this represents a time entry.  Sent when phone is removed from mobile away.

# refpage for request.post()
# very simple.

# import adafruit_requests as requests

# flask server on 3B1 (mobileAway-raspi-side.py)
# TODO: See PORT in mobileAway-raspi-side.py
URL_entry = 'http://RASPI-IP:PORT/mba-entry'
URL_select = 'http://RASPI-IP:PORT/mba-select'


def postTimeEntryTo3B1(points, bonus, duration, requests):
    """
    post
    points, bonus and duration to flask server on 3B1
    """
    data = {
        'points': points,
        'bonus': bonus,
        'duration': duration
    }
    response = requests.post(URL_entry, json=data)
    print('postTimeEntryTo3B1() status code:', response.status_code)


def getDataByFrom3B1(select_by, requests):
    """
    post
    select_by='today'/'this_month' to flask server on 3B1 and get list of
    (points, bonus, duration) in pbds
    """
    data = {
        'select_by': select_by
    }

    response = requests.post(URL_select, json=data)
    # print('HOWTHISLOOKS?', response)

    print('getDataByFrom3B1() select_by:', select_by)
    print('getDataByFrom3B1() status code:', response.status_code)
    print('getDataByFrom3B1() json:', response.json())
    # print('getDataByFrom3B1() json:', type(response.json()['pbds']))  # list!
    # inner tuple is converted to list
    # print('getDataByFrom3B1() json:', response.json()['pbds'][0])
    # print('getDataByFrom3B1() json:', type(response.json()['pbds'][0]))

    return response.json()['pbds']
