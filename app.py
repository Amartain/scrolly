import json
import os
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

DATA_DIR = "data"
CURRENT_FILE = os.path.join(DATA_DIR, "current_day.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
FUTURE_FILE = os.path.join(DATA_DIR, "future_trials.json")
RITUALS_FILE = os.path.join(DATA_DIR, "rituals.json")
RESTORATIONS_FILE = os.path.join(DATA_DIR, "restorations.json")

def ensure_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    for file in [CURRENT_FILE, HISTORY_FILE, FUTURE_FILE, RITUALS_FILE, RESTORATIONS_FILE]:
        if not os.path.exists(file):
            with open(file, 'w', encoding='utf-8') as f:
                json.dump([], f)

def get_logical_date(dt=None):
    if dt is None: 
        dt = datetime.now().astimezone()
    if dt.hour < 4: 
        dt = dt - timedelta(days=1)
    return dt.strftime("%Y-%m-%d")

def perform_rollover():
    ensure_data()
    with open(CURRENT_FILE, 'r', encoding='utf-8') as f:
        try: current = json.load(f)
        except json.JSONDecodeError: current = []
        
    today_logical = get_logical_date()
    active, archive, mandates_to_horizon = [], [], []
    
    for q in current:
        if q.get("logical_date") != today_logical:
            if q.get("status") not in ["Done", "Cancelled"]:
                if q.get("mandate"):
                    q["status"] = "Remaining"
                    q["logical_date"] = today_logical
                    mandates_to_horizon.append(q)
                    continue
                else:
                    q["status"] = "Cancelled"
            archive.append(q)
        else:
            active.append(q)
            
    if mandates_to_horizon:
        with open(FUTURE_FILE, 'r', encoding='utf-8') as f:
            try: future = json.load(f)
            except json.JSONDecodeError: future = []
        future = mandates_to_horizon + future
        with open(FUTURE_FILE, 'w', encoding='utf-8') as f:
            json.dump(future, f, indent=4)
            
    if archive:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try: history = json.load(f)
            except json.JSONDecodeError: history = []
        history.extend(archive)
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4)
            
    with open(CURRENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(active, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dev-log')
def dev_log():
    return render_template('dev_log.html')

@app.route('/api/state', methods=['GET'])
def get_state():
    perform_rollover()
    with open(CURRENT_FILE, 'r', encoding='utf-8') as f: current = json.load(f)
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f: history = json.load(f)
    with open(FUTURE_FILE, 'r', encoding='utf-8') as f: future = json.load(f)
    with open(RITUALS_FILE, 'r', encoding='utf-8') as f: rituals = json.load(f)
    with open(RESTORATIONS_FILE, 'r', encoding='utf-8') as f: restorations = json.load(f)
    return jsonify({"current": current, "history": history, "future": future, "rituals": rituals, "restorations": restorations})

@app.route('/api/save', methods=['POST'])
def save_state():
    data = request.json
    if isinstance(data, list):
        current_data = data
        future_data = None
        rituals_data = None
        restorations_data = None
    else:
        current_data = data.get('current', [])
        future_data = data.get('future', [])
        rituals_data = data.get('rituals', [])
        restorations_data = data.get('restorations', [])
        
    with open(CURRENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, indent=4)
        
    if future_data is not None:
        with open(FUTURE_FILE, 'w', encoding='utf-8') as f:
            json.dump(future_data, f, indent=4)
            
    if rituals_data is not None:
        with open(RITUALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(rituals_data, f, indent=4)
            
    if restorations_data is not None:
        with open(RESTORATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(restorations_data, f, indent=4)
            
    return jsonify({"status": "success"})

@app.route('/api/import', methods=['POST'])
def import_state():
    data = request.json
    if 'current' in data:
        with open(CURRENT_FILE, 'w', encoding='utf-8') as f: json.dump(data['current'], f, indent=4)
    if 'history' in data:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f: json.dump(data['history'], f, indent=4)
    if 'future' in data:
        with open(FUTURE_FILE, 'w', encoding='utf-8') as f: json.dump(data['future'], f, indent=4)
    if 'rituals' in data:
        with open(RITUALS_FILE, 'w', encoding='utf-8') as f: json.dump(data['rituals'], f, indent=4)
    if 'restorations' in data:
        with open(RESTORATIONS_FILE, 'w', encoding='utf-8') as f: json.dump(data['restorations'], f, indent=4)
    return jsonify({"status": "success"})

@app.route('/api/purge', methods=['POST'])
def purge_state():
    with open(CURRENT_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, indent=4)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    ensure_data()
    app.run(debug=True, port=5000)