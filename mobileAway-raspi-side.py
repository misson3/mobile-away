# ========================================================== this is for GitHub
# Feb22,2022
# mobileAway-raspi-side.py
# ref is my previous code,
# timetracker_in-and-out_to_db.py

from datetime import datetime
from flask import Flask
from flask import jsonify
from flask import request
import mysql.connector
from secrets import secrets  # my


# === instantiate flask server ===
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
'''
according to https://flask.palletsprojects.com/en/0.12.x/config/
By default Flask serialize object to ascii-encoded JSON.
If this is set to False Flask will not encode to ASCII and
output strings as-is and return unicode strings.
jsonify will automatically encode it in utf-8 then for
transport for instance.
'''


# ---------------------
# inserting data to db
# ---------------------
@app.route('/mba-entry', methods=['POST'])
def reception():
    """
    mba: mobile away
    """
    print("\n=== POST received from mobile away! ===")
    print("request.json is shown below.")
    print(request.json)
    # print(type(request.json))
    # print(type(jsonify(request.json)))
    # return json.dumps(request.json)

    points = request.json['points']
    bonus = request.json['bonus']
    duration = request.json['duration']

    insertMBATimeEntry(points, bonus, duration)

    return jsonify(request.json)


# db handling functions
def insertMBATimeEntry(points, bonus, duration):
    db_host = 'localhost'
    db_name = 'mobile_away'
    db_user = secrets['db-user']
    db_pass = secrets['db-passwd']

    # create timestamp
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = mysql.connector.connect(
            user=db_user,
            password=db_pass,
            host=db_host,
            database=db_name)

    try:
        cur = conn.cursor()
        sql = "INSERT INTO time_entries "
        sql += "(points, bonus, duration, timestamp) "
        sql += "VALUES (%s, %s, %s, %s)"
        values = [points, bonus, duration, ts]
        cur.execute(sql, values)
        # do not forget this!!!
        conn.commit()
    except Exception as e:
        print("!!! Exception !!!")
        print("type():", type(e))
        print("e", e)
    finally:
        cur.close()
        conn.close()

    print("insertMBATimeEntry() done.")


# --------------------------------
# selecting data by date or month
# --------------------------------
@app.route('/mba-select', methods=['POST'])
def datadesk():
    """
    mba: mobile away
    """
    print("\n=== POST received from mobile away! ===")
    print("request.json is shown below.")
    print(request.json)
    # print(type(request.json))
    # print(type(jsonify(request.json)))
    # return json.dumps(request.json)

    select_by = request.json['select_by']  # 'today' or 'this_month'

    print('###### select_by', select_by)

    pbds = selectMBATimeEntry(select_by)

    print('###### pbds', pbds)

    # pack the pbds in the json to return.
    # pbds itself (python list) can not be returned as it is.
    # unpack the pbds on the receiver side.
    request.json['pbds'] = pbds

    return jsonify(request.json)


def selectMBATimeEntry(select_by):
    """
    select_by: 'today' or 'this_month'
    """
    db_host = 'localhost'
    db_name = 'mobile_away'
    db_user = secrets['db-user']
    db_pass = secrets['db-passwd']

    conn = mysql.connector.connect(
            user=db_user,
            password=db_pass,
            host=db_host,
            database=db_name)
    cur = conn.cursor()

    pbds = [(0, 0, 0)]  # list of (points, bonus, duration)
    # i put dummy (0, 0, 0) in case cur is empty
    try:
        sql = "SELECT * "
        sql += "FROM time_entries "
        if select_by == 'today':
            sql += "WHERE datediff(timestamp, curdate()) = 0"
        elif select_by == 'this_month':
            sql += "WHERE month(timestamp) = month(curdate())"
        cur.execute(sql)
        for raw in cur:
            pbds.append((raw[1], raw[2], raw[3]))  # appending tuple
    except Exception as e:
        print("!!! Exception !!!")
        print("type():", type(e))
        print("e", e)
    finally:
        cur.close()
        conn.close()

    print("selectMBATimeEntry() done.")

    return pbds


if __name__ == "__main__":
    # TODO: set port
    app.run(host='0.0.0.0', port=00000, debug=True)
    # MEMO: change this port if other server port is active on the raspi.
