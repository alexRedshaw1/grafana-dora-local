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

@app.route('/search', methods=['POST', 'GET'])
def search():
    # Return available metrics
    metrics = [
        "time_spent",
        "remaining_estimate",
        "original_estimate",
        "comment_count",
        "attachment_count",
        "worklog_entries"
    ]
    return jsonify(metrics)

@app.route('/metrics/<metric_name>', methods=['GET'])
def get_metric(metric_name):
    data = load_jira_data()
    
    # Get the timestamp from the most recent update or worklog
    timestamp = None
    if data['fields'].get('worklog', []):
        timestamp = datetime.strptime(
            data['fields']['worklog'][0]['updated'],
            "%Y-%m-%dT%H:%M:%S.%f%z"
        ).timestamp() * 1000
    
    response = {}
    
    if metric_name == 'time_spent':
        response['value'] = data['fields']['timetracking']['timeSpentSeconds']
        response['formatted_time'] = data['fields']['timetracking']['timeSpent']
    
    elif metric_name == 'remaining_estimate':
        response['value'] = data['fields']['timetracking']['remainingEstimateSeconds']
        response['formatted_time'] = data['fields']['timetracking']['remainingEstimate']
    
    elif metric_name == 'original_estimate':
        response['value'] = data['fields']['timetracking']['originalEstimateSeconds']
        response['formatted_time'] = data['fields']['timetracking']['originalEstimate']
    
    elif metric_name == 'comment_count':
        response['value'] = len(data['fields'].get('comment', []))
    
    elif metric_name == 'attachment_count':
        response['value'] = len(data['fields'].get('attachment', []))
    
    elif metric_name == 'worklog_entries':
        response['value'] = len(data['fields'].get('worklog', []))
    
    else:
        return jsonify({"error": "Metric not found"}), 404

    response['timestamp'] = timestamp
    return jsonify(response)

# Original POST query endpoint remains for Grafana compatibility
@app.route('/query', methods=['POST'])
def query():
    data = load_jira_data()
    req_data = request.get_json()
    target = req_data.get('target', 'time_spent')
    
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
    app.run(host='0.0.0.0', port=3001, debug=True)