# api_server.py
from flask import Flask, jsonify, request
import json
from datetime import datetime

app = Flask(__name__)

def load_jira_data():
    with open('./data/jira_example_data.json', 'r') as f:
        return json.load(f)

@app.route('/')
def health():
    return jsonify({"status": "ok"})

@app.route('/search', methods=['POST'])
def search():
    # Return available metrics
    return jsonify([
        "time_spent",
        "remaining_estimate",
        "original_estimate",
        "comment_count",
        "attachment_count",
        "worklog_entries",
    ])

@app.route('/query', methods=['POST'])
def query():
    data = load_jira_data()
    req_data = request.get_json()
    target = req_data.get('target', 'time_spent')
    
    # Get the timestamp from the most recent update or worklog
    timestamp = None
    if data['fields'].get('worklog', []):
        timestamp = datetime.strptime(
            data['fields']['worklog'][0]['updated'],
            "%Y-%m-%dT%H:%M:%S.%f%z"
        ).timestamp() * 1000
    
    response = []
    
    if target == 'time_spent':
        response.append({
            'target': 'Time Spent',
            'datapoints': [[data['fields']['timetracking']['timeSpentSeconds'], timestamp]]
        })
    
    elif target == 'remaining_estimate':
        response.append({
            'target': 'Remaining Estimate',
            'datapoints': [[data['fields']['timetracking']['remainingEstimateSeconds'], timestamp]]
        })
    
    elif target == 'original_estimate':
        response.append({
            'target': 'Original Estimate',
            'datapoints': [[data['fields']['timetracking']['originalEstimateSeconds'], timestamp]]
        })
    
    elif target == 'comment_count':
        response.append({
            'target': 'Comment Count',
            'datapoints': [[len(data['fields'].get('comment', [])), timestamp]]
        })
    
    elif target == 'attachment_count':
        response.append({
            'target': 'Attachment Count',
            'datapoints': [[len(data['fields'].get('attachment', [])), timestamp]]
        })
    
    elif target == 'worklog_entries':
        response.append({
            'target': 'Worklog Entries',
            'datapoints': [[len(data['fields'].get('worklog', [])), timestamp]]
        })
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)