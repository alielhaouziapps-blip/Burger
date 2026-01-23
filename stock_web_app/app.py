from flask import Flask, render_template, Response
from simulator import run_simulation
import json
import pandas as pd

app = Flask(__name__)

# Helper to sanitize nested dictionaries/lists
def sanitize_data(obj):
    if isinstance(obj, dict):
        return {k: sanitize_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_data(x) for x in obj]
    elif isinstance(obj, float):
        # pd.isna catches both np.nan and None
        return None if pd.isna(obj) else obj
    return obj

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate')
def simulate():
    raw_data = run_simulation()

    # 1. Sanitize the entire dictionary recursively
    clean_data = sanitize_data(raw_data)

    # 2. Serialize to string
    try:
        json_output = json.dumps(clean_data, allow_nan=False)
    except ValueError:
        # Fallback for safety
        json_output = json.dumps(clean_data).replace('NaN', 'null')

    return Response(json_output, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
