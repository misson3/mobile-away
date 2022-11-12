# Nov12, 2022, ms  Modified for the simpler version
# Nov24, 2021, ms
# toggltrack.py

# functions for toggl API

import json
# import adafruit_datetime


def startTimeEntry(requests, desc, pid, wid, auth):
    """
    desc: description for the entry
    pid: project id
    wid: workspace id
    """
    print("##### startTimeEntry()")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth
    }

    data = '{"time_entry":{"description":"' + desc + '",'
    data += '"pid":' + pid + ','
    data += '"wid":' + wid + ','
    data += '"created_with":"curl"}' + '}'
    print('[debug] header')
    print(headers)
    print('[debug] data')
    print(data)

    uri = 'https://api.track.toggl.com/api/v8/time_entries/start'
    # response = requests.post(uri,
    #                          headers=headers, data=data,
    #                          auth=(auth, 'api_token'))
    response = requests.post(uri, headers=headers, data=data)
    print('[debug] response.status_code')
    print(response.status_code)
    print('[debug] response.text')
    print(response.text)
    print()
    py_dict = json.loads(response.text)
    entry_id = py_dict['data']['id']
    print('[debug] time entry id:', entry_id)
    utc_start_iso = py_dict['data']['start'][:-1]
    print('[debug] utc_start_iso:', utc_start_iso)
    print()

    return entry_id, utc_start_iso


def stopTimeEntry(requests, entry_id, auth):
    """
    stop is easier.  just include entry_id in the uri
    """
    print("##### stopTimeEntry()")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth,
        'Content-length': "0"
    }

    uri = 'https://api.track.toggl.com/api/v8/time_entries/'
    uri += str(entry_id) + '/stop'

    print()
    print('[debug] header')
    print(headers)
    print('[debug] uri')
    print(uri)
    # response = requests.put(uri,
    #                         headers=headers,
    #                         auth=(auth, 'api_token'))
    response = requests.put(uri, headers=headers)

    print('[debug] response.text')
    print(response.text)
    py_dict = json.loads(response.text)
    utc_stop_iso = py_dict['data']['stop'].split('+')[0]
    print('[debug] utc_stop_iso:', utc_stop_iso)
    print()

    return utc_stop_iso


if __name__ == '__main__':
    pass
