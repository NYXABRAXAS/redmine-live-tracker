from flask import Flask, send_from_directory, jsonify
import urllib.request
import json
import os
from concurrent.futures import ThreadPoolExecutor
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Professional branding for Prohorizon Digitech Solution
REDMINE_URL = "https://redmine.prohorizon.in:3000"
API_KEY = "16eac9e2365e5e3b2f398ee4b16dd30f815d2dd7"
BASE_API = f"{REDMINE_URL}/issues.json?status_id=*&key={API_KEY}"

def fetch_page(offset):
    url = f"{BASE_API}&limit=100&offset={offset}"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return json.loads(response.read())
    except Exception:
        return None

@app.route('/api/issues')
def get_issues():
    first_page = fetch_page(0)
    if not first_page:
        return jsonify({"error": "Failed to fetch data"}), 500

    total_count = first_page.get("total_count", 0)
    all_issues = first_page.get("issues", [])
    offsets = range(100, total_count, 100)

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_page, offsets))

    for res in results:
        if res:
            all_issues.extend(res.get("issues", []))

    return jsonify({"issues": all_issues})

@app.route('/')
def index():
    # MUST MATCH THE HTML FILENAME
    return send_from_directory('.', 'index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
