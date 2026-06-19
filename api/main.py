
from flask import Flask, jsonify, request, render_template
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import random

load_dotenv()
MASTER_AUTH = os.getenv("API_MASTER_AUTH")

app = Flask(__name__)

PROJECT_FOLDER = os.getcwd()
API_FOLDER = f"{PROJECT_FOLDER}"
UPLOAD_FOLDER = f"{API_FOLDER}/static"

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



with app.app_context():
    errors = {
        "MISSING_AUTH": (jsonify({"error": "missing auth header :("}), 401),
        "MAlFORMED_AUTH": (jsonify({"error": "malformed auth header :("}), 401),
        "INVALID_TOKEN_TYPE": (jsonify({"error": "invalid token type, must be Bearer :("}), 401),
        "INVALID_AUTH": (jsonify({"error": "invalid auth :("}), 401),

        # COTD
        "COTD_EXISTS": (jsonify({"error": "creature of the day entry already exists for today :("}), 403), # NOT USED ANYMORE
        "COTD_MALFORMED_JSON": (jsonify({"error": "cotd entry must have the keys: 'title', 'description', and optional:'date' (yyyy-mm-dd e.g. '2026-06-10') :("}), 401)
    }

def auth_check():
    with app.app_context():
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return errors["MISSING_AUTH"]
        try:
            header_type, token = auth_header.split(" ")
            if header_type.lower() != 'bearer':
                return errors["INVALID_TOKEN_TYPE"]
            return token == MASTER_AUTH
        except ValueError:
            return errors["MAlFORMED_AUTH"]

# check whether auth is master auth # NOTE don't use - it doesn't work, always passes for some reasons??
def determine_auth():
    with app.app_context():
        if not auth_check(): return errors["INVALID_AUTH"]


# check whether json/dict contains key
def key_exists(js, key):
    return key in js.keys()


######################################################
#############           ROUTES           #############
###################################################### 

@app.route('/api/test', methods=["POST"])
def test():
    master_auth = auth_check()
    
    json = request.get_json()

    res = {
        "message": "heard you loud and clear. your json is in the json field. master_auth specifies whether your auth token is the same as the master one",
        "master_auth": master_auth,
        "json": json
    }
    return jsonify(res), 200

@app.route('/api/documentation', methods=["GET"])
def documentation():
    return render_template('documentation.html')

@app.route('/api/greeting', methods=["GET"])
def greeting():
    res = {
        "message": random.choice([
            "howdy!", "hello!", "greetings!",
            "hello there", "hi", "yello"
        ])
    }
    return jsonify(res), 200

# COTD ###############################################

COTD_DIR = f"{API_FOLDER}/cotd"
COTD_FILE = f"{COTD_DIR}/cotd.json"
COTD_MEDIA = f"{COTD_DIR}/media"

def date_malformed(date):
    date_parts = date.split("-")
    if len(date_parts) != 3: return True
    if not (date_parts[0].isnumeric() and len(date_parts[0]) == 4): return True
    if not (date_parts[1].isnumeric() and len(date_parts[1]) == 2): return True
    if not (date_parts[2].isnumeric() and len(date_parts[2]) == 2): return True
    return False

def get_date_if_none(js):
    todays_date = True
    if key_exists(js, "date"):
        date = js["date"]
        todays_date = False
    else:
        date = str(datetime.now().date())
    if date_malformed(date): # if malformed
        return False, todays_date
    else:
        return date, todays_date

@app.route('/api/cotd/upload', methods=["POST"])
def cotd_upload():
    if not auth_check(): return errors["INVALID_AUTH"]


    try:
        js = json.loads(request.form.get('data', '{}'))
    except json.JSONDecodeError:
        return errors["COTD_MALFORMED_JSON"]
    
    print(js)


    for key in ["title", "description"]:
        if not key_exists(js, key):
            return errors["COTD_MALFORMED_JSON"]

    with open(COTD_FILE, "r") as f:
        cotd_data = json.loads(f.read())

    date, is_today = get_date_if_none(js)
    if not date:
        return errors["COTD_MALFORMED_JSON"]

    submission_existed = key_exists(cotd_data, date)
    if submission_existed:
        entry_no = len(cotd_data.keys())
    else:
        entry_no = len(cotd_data.keys()) + 1

    if 'image' not in request.files:
        return jsonify({"error": "no image attached :("}), 400
    file = request.files['image']
    filename = f"{entry_no}_{date}.png"
    file.filename = filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], "cotd", filename)
    file.save(filepath)

    cotd_data[date] = {
        "title": js["title"],
        "description": js["description"],
        "entry_no": entry_no,
        "media": f"/static/cotd/{file.filename}"
    }

    with open(COTD_FILE, "w") as f:
        f.write(json.dumps(cotd_data, indent=4))

    if submission_existed:
        res = {"message": "updated creature of the day successfully :)"}
    else:
        res = {"message": "submitted creature of the day successfully :)"}

    return jsonify(res), 201

@app.route('/api/cotd/edit', methods=["POST"])
def cotd_edit_fields():
    if not auth_check(): return errors["INVALID_AUTH"]
    js = request.get_json()

    date, is_today = get_date_if_none(js)
    if not date:
        return errors["COTD_MALFORMED_JSON"]
    
    with open(COTD_FILE, "r") as f:
        cotd_data = json.loads(f.read())

    if date in cotd_data.keys():
        pass
    elif is_today: # no entry exists for today
        return jsonify({"error": f"no entry exists for today :("}), 403
    else: # no entry exists for specified date
        return jsonify({"error": f"no entry exists for '{date}' :("}), 403

    # update only the fields the user provided
    edited_fileds = []
    for key in ["title", "description", "entry_no"]:
        if key_exists(js, key):
            cotd_data[date][key] = js[key]
            edited_fileds.append(key)

    if len(edited_fileds) == 0:
        return jsonify({"error": "no fields were specified :("}), 401

    with open(COTD_FILE, "w") as f:
        f.write(json.dumps(cotd_data, indent=4))
    
    return jsonify({"message": f"updated fields: {", ".join([f"'{x}'" for x in edited_fileds])} :)"})

@app.route('/api/cotd/delete', methods=["DELETE"])
def cotd_delete():
    if not auth_check(): return errors["INVALID_AUTH"]
    js = request.get_json()

    date, is_today = get_date_if_none(js)
    if not date:
        return errors["COTD_MALFORMED_JSON"]
    
    with open(COTD_FILE, "r") as f:
        cotd_data = json.loads(f.read())

    if date in cotd_data.keys():
        pass
    elif is_today: # either no entry exists for today, or has already been deleted
        return jsonify({"error": f"either no entry existed for today, or it has already been deleted :("}), 403
    else: # either no entry exists for specified date, or has already been deleted
        return jsonify({"error": f"either no entry existed for '{date}', or it has already been deleted  :("}), 403
    
    cotd_data.pop(date)

    with open(COTD_FILE, "w") as f:
        f.write(json.dumps(cotd_data, indent=4))

    return jsonify({"message": f"successfully deleted entry '{date}' :)"}), 200

@app.route('/api/cotd/get', methods=["GET"])
def cotd_get():
    js = request.get_json()

    with open(COTD_FILE, "r") as f:
        cotd_data = json.loads(f.read())

    if key_exists(js, "date"):
        date = js["date"]
        if date in cotd_data.keys():
            if date_malformed(date):
                return jsonify({"error": "date malformed. should be yyyy-mm-dd e.g 6942-06-09 :("}), 401
            else:
                cotd_entry = cotd_data[js["date"]]
        else:
            return jsonify({"error": f"no creature of the day for '{date}' :("}), 403
    else:
        return jsonify({"error": "failed to provide the 'date' field :("}), 401

    return jsonify(cotd_entry), 200

@app.route('/api/cotd/get_today', methods=["GET"])
def cotd_get_today():
    date = str(datetime.now().date())
    with open(COTD_FILE, "r") as f:
        cotd_data = json.loads(f.read())
    if date in cotd_data.keys():
        todays_cotd_data = cotd_data[date]
    else:
        return jsonify({"error": "no creature of the day yet :("}), 403
    return jsonify(todays_cotd_data), 200



######################################################
#############         ROUTES END         #############
###################################################### 

if __name__ == "__main__":
    app.run(debug=True, port=5000)