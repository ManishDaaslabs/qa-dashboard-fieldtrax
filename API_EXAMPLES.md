# QA Analytics Platform - API Examples

Complete guide to using the QA Analytics Platform API with real examples.

---

## 📋 Table of Contents

1. [Setup](#setup)
2. [Health Check](#health-check)
3. [Data Upload](#data-upload)
4. [Dashboard Summary](#dashboard-summary)
5. [Test Executions](#test-executions)
6. [Forecasting](#forecasting)
7. [Anomaly Detection](#anomaly-detection)
8. [Risk Assessment](#risk-assessment)
9. [Root Cause Analysis](#root-cause-analysis)
10. [Defects Management](#defects-management)
11. [Full Dashboard](#full-dashboard)

---

## Setup

**Base URL:** `http://localhost:5000`

### Using curl

```bash
BASE_URL="http://localhost:5000"
```

### Using Python requests

```python
import requests
import json

BASE_URL = "http://localhost:5000"

def make_request(method, endpoint, **kwargs):
    url = f"{BASE_URL}{endpoint}"
    response = requests.request(method, url, **kwargs)
    return response.json()
```

### Using JavaScript/Node.js

```javascript
const BASE_URL = "http://localhost:5000";

async function makeRequest(endpoint, options = {}) {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  return response.json();
}
```

---

## Health Check

Verify the API is running.

### Request

```bash
curl -X GET http://localhost:5000/api/health
```

### Python

```python
response = make_request("GET", "/api/health")
print(response)
```

### Response

```json
{
  "status": "healthy",
  "timestamp": "2026-09-04T10:30:45.123456",
  "version": "2.0.0"
}
```

---

## Data Upload

Upload CSV or Excel files containing test execution data.

### Required CSV/Excel Columns

| Column | Type | Example |
|--------|------|---------|
| FEATURE | String | "DraftJob" |
| TOTAL TESTS | Integer | 57 |
| PASSED | Integer | 53 |
| FAILED | Integer | 4 |
| PENDING | Integer | 0 |
| PASS RATE % | Float | 93.0 |
| DEFECTS | Integer | 3 |
| RISK LEVEL | String | "High" |

### Request

```bash
curl -X POST \
  -F "file=@test_execution_report.xlsx" \
  http://localhost:5000/api/upload
```

### Python

```python
with open("test_execution_report.xlsx", "rb") as f:
    files = {"file": f}
    response = make_request("POST", "/api/upload", files=files)
    print(response)
```

### JavaScript

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);

const response = await fetch(`${BASE_URL}/api/upload`, {
  method: "POST",
  body: formData
});
const data = await response.json();
console.log(data);
```

### Response

```json
{
  "status": "success",
  "message": "Successfully imported 42 records",
  "records_inserted": 42
}
```

### Error Response

```json
{
  "error": "Unsupported file format. Use .xlsx or .csv"
}
```

---

## Dashboard Summary

Get overall QA metrics and status.

### Request

```bash
curl -X GET http://localhost:5000/api/summary
```

### Python

```python
response = make_request("GET", "/api/summary")
summary = response["summary"]
print(f"Pass Rate: {summary['pass_rate']}%")
print(f"Critical Features: {summary['critical_features']}")
```

### Response

```json
{
  "summary": {
    "total_tests": 427,
    "passed": 202,
    "failed": 49,
    "pending": 176,
    "pass_rate": 47.3,
    "health_score": 27.3,
    "critical_features": 3,
    "high_risk_features": 5,
    "total_defects": 10,
    "last_updated": "2026-09-04T10:30:00.000000"
  },
  "features": {
    "DraftJob": "High",
    "BranchOverhead": "High",
    "Break_Types_and_No_Show": "Critical",
    "Recall_a_dispatch": "Critical",
    "ProjectGroupings": "Critical",
    "Warehouse_Overhead": "High",
    "ReadyToWork": "Critical",
    "TaskGrouping": "High"
  }
}
```

---

## Test Executions

Retrieve test execution history with optional filtering.

### Get All Tests (Last 30 Days)

```bash
curl -X GET http://localhost:5000/api/tests?days=30
```

### Filter by Feature

```bash
curl -X GET "http://localhost:5000/api/tests?feature=DraftJob&days=30"
```

### Python

```python
# Get all tests
response = make_request("GET", "/api/tests", params={"days": 30})
tests = response["data"]

# Filter by feature
response = make_request("GET", "/api/tests", params={
    "feature": "DraftJob",
    "days": 30
})
```

### Response

```json
{
  "total": 15,
  "data": [
    {
      "id": 1,
      "feature_name": "DraftJob",
      "total_tests": 57,
      "passed": 53,
      "failed": 4,
      "pending": 0,
      "pass_rate": 93.0,
      "execution_date": "2026-09-04T10:00:00",
      "defects_count": 3,
      "risk_level": "High"
    },
    ...
  ]
}
```

---

## Forecasting

Get 7-day ahead pass rate predictions.

### Request

```bash
curl -X GET http://localhost:5000/api/forecast/DraftJob?days=7
```

### Python

```python
response = make_request("GET", "/api/forecast/DraftJob", params={"days": 7})
forecast = response["forecast"]

for prediction in forecast:
    print(f"{prediction['date']}: {prediction['predicted_pass_rate']}% "
          f"(confidence: {prediction['confidence']})")
```

### Response

```json
{
  "feature": "DraftJob",
  "forecast": [
    {
      "date": "2026-09-05T00:00:00",
      "predicted_pass_rate": 94.2,
      "confidence": 0.87
    },
    {
      "date": "2026-09-06T00:00:00",
      "predicted_pass_rate": 94.5,
      "confidence": 0.86
    },
    {
      "date": "2026-09-07T00:00:00",
      "predicted_pass_rate": 94.8,
      "confidence": 0.85
    },
    ...
  ],
  "trend": "improving",
  "average_forecast": 94.5
}
```

---

## Anomaly Detection

Identify unusual patterns in test execution.

### Request

```bash
curl -X GET "http://localhost:5000/api/anomalies?days=30"
```

### Python

```python
response = make_request("GET", "/api/anomalies", params={"days": 30})

print(f"Total anomalies: {response['total_anomalies']}")
for anomaly in response['anomalies']:
    print(f"\n{anomaly['feature']}")
    print(f"  Reason: {anomaly['reason']}")
    print(f"  Severity: {anomaly['severity']}")
    print(f"  Score: {anomaly['anomaly_score']}")
```

### Response

```json
{
  "total_anomalies": 2,
  "period_days": 30,
  "anomalies": [
    {
      "feature": "Break_Types_and_No_Show",
      "date": "2026-09-02T10:00:00",
      "anomaly_score": -0.45,
      "reason": "Unusual pattern detected - Pass rate: 30.2%, Failed tests: 8",
      "severity": "High"
    },
    {
      "feature": "ProjectGroupings",
      "date": "2026-08-28T10:00:00",
      "anomaly_score": -0.38,
      "reason": "Unusual pattern detected - Pass rate: 20.6%, Failed tests: 8",
      "severity": "High"
    }
  ]
}
```

---

## Risk Assessment

Get risk prediction for specific features.

### Request

```bash
curl -X GET http://localhost:5000/api/risk/DraftJob
```

### Python

```python
response = make_request("GET", "/api/risk/DraftJob")

print(f"Feature: {response['feature']}")
print(f"Risk Level: {response['risk_level']}")
print(f"Risk Score: {response['risk_score']}/1.0")
print(f"Pass Rate: {response['pass_rate']}%")
print("\nRecommendations:")
for rec in response['recommendations']:
    print(f"  - {rec}")
```

### Response

```json
{
  "feature": "DraftJob",
  "risk_score": 0.35,
  "risk_level": "High",
  "pass_rate": 93.0,
  "recommendations": [
    "High failure rate detected. Review test design and environment."
  ]
}
```

### Risk Levels

| Risk Level | Score Range | Meaning |
|-----------|------------|---------|
| Low | 0.0 - 0.4 | Feature is stable |
| High | 0.4 - 0.6 | Feature needs attention |
| Critical | 0.6 - 1.0 | Immediate action required |

---

## Root Cause Analysis

Analyze why tests are failing.

### Request

```bash
curl -X GET "http://localhost:5000/api/rootcause/DraftJob?days=30"
```

### Python

```python
response = make_request("GET", "/api/rootcause/DraftJob", params={"days": 30})

print(f"Feature: {response['feature']}")
print(f"Analysis Period: {response['period_days']} days")
print(f"Average Pass Rate: {response['average_pass_rate']}%")
print(f"Failure Trend: {response['failure_trend']}")
print(f"\nInsights:")
for insight in response['insights']:
    print(f"  • {insight}")
```

### Response

```json
{
  "feature": "DraftJob",
  "period_days": 30,
  "total_executions": 12,
  "average_pass_rate": 92.1,
  "average_failures": 4.7,
  "failure_trend": "decreasing",
  "variance_in_failures": 1.2,
  "correlation_failures_to_pending": 0.15,
  "insights": [
    "Pass rate declining over time - investigate recent changes"
  ]
}
```

---

## Defects Management

Retrieve and filter defects.

### Get All Defects

```bash
curl -X GET http://localhost:5000/api/defects
```

### Filter by Feature

```bash
curl -X GET "http://localhost:5000/api/defects?feature=DraftJob"
```

### Filter by Severity

```bash
curl -X GET "http://localhost:5000/api/defects?severity=Medium"
```

### Python

```python
# Get all defects
response = make_request("GET", "/api/defects")

# Group by severity
from collections import defaultdict
by_severity = defaultdict(list)
for defect in response["data"]:
    by_severity[defect["severity"]].append(defect)

for severity, defects in by_severity.items():
    print(f"\n{severity} ({len(defects)} defects):")
    for d in defects:
        print(f"  {d['defect_id']}: {d['summary']}")
```

### Response

```json
{
  "total": 10,
  "data": [
    {
      "id": 1,
      "defect_id": "BUG-01",
      "severity": "Low",
      "priority": "P3",
      "summary": "Minor UI text issue",
      "feature": "DraftJob",
      "status": "New",
      "created_date": "2026-09-01T10:00:00"
    },
    ...
  ]
}
```

---

## Full Dashboard

Get complete dashboard data in one request.

### Request

```bash
curl -X GET "http://localhost:5000/api/dashboard?days=30"
```

### Python

```python
response = make_request("GET", "/api/dashboard", params={"days": 30})

# Access all dashboard sections
summary = response["summary"]
features = response["features"]
executions = response["executions"]
anomalies = response["anomalies"]
forecasts = response["forecasts"]
timestamp = response["timestamp"]

print(f"Dashboard updated at: {timestamp}")
print(f"Pass rate: {summary['pass_rate']}%")
print(f"Health score: {summary['health_score']}/100")
print(f"Anomalies detected: {len(anomalies)}")
print(f"Features with forecasts: {len(forecasts)}")
```

### Response

```json
{
  "summary": { ...full summary... },
  "features": { ...feature risks... },
  "executions": [ ...recent test executions... ],
  "anomalies": [ ...detected anomalies... ],
  "forecasts": { ...pass rate forecasts... },
  "timestamp": "2026-09-04T10:30:45.123456"
}
```

---

## Advanced Scenarios

### Scenario 1: Monitor a Critical Feature

```python
import time

def monitor_feature(feature_name, check_interval=60):
    while True:
        # Get risk assessment
        risk = make_request("GET", f"/api/risk/{feature_name}")
        
        # Get forecast
        forecast = make_request("GET", f"/api/forecast/{feature_name}")
        
        print(f"\n{feature_name}")
        print(f"Risk: {risk['risk_level']} ({risk['risk_score']}/1.0)")
        print(f"Pass Rate: {risk['pass_rate']}%")
        print(f"Trend: {forecast['trend']}")
        
        if risk['risk_level'] == 'Critical':
            print("⚠️ ALERT: Critical risk detected!")
            # Send notification, log, etc.
        
        time.sleep(check_interval)

# Start monitoring
monitor_feature("DraftJob")
```

### Scenario 2: Export Data to CSV

```python
import csv
from datetime import datetime

response = make_request("GET", "/api/tests", params={"days": 30})

filename = f"test_data_{datetime.now().strftime('%Y%m%d')}.csv"
with open(filename, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=response["data"][0].keys())
    writer.writeheader()
    writer.writerows(response["data"])

print(f"Data exported to {filename}")
```

### Scenario 3: Generate Report

```python
from datetime import datetime

def generate_report(days=30):
    summary = make_request("GET", "/api/summary")["summary"]
    anomalies = make_request("GET", "/api/anomalies", params={"days": days})
    
    report = f"""
    QA Analytics Report
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Period: Last {days} days
    
    Summary:
    - Total Tests: {summary['total_tests']}
    - Pass Rate: {summary['pass_rate']}%
    - Health Score: {summary['health_score']}/100
    - Critical Features: {summary['critical_features']}
    - Active Defects: {summary['total_defects']}
    
    Anomalies Detected: {anomalies['total_anomalies']}
    """
    
    return report

print(generate_report(days=30))
```

---

## Error Handling

### Common Error Responses

```json
{
  "error": "Feature not found"
}
```

```json
{
  "error": "No file provided"
}
```

```json
{
  "error": "Unsupported file format"
}
```

### Python Error Handling

```python
try:
    response = make_request("GET", f"/api/risk/{feature}")
    if "error" in response:
        print(f"API Error: {response['error']}")
    else:
        print(f"Risk: {response['risk_level']}")
except Exception as e:
    print(f"Request failed: {e}")
```

---

## Rate Limiting & Performance

- **Upload file size limit:** 50MB
- **Default lookback period:** 30 days
- **Forecast horizon:** 7 days
- **API response time:** < 1s for most endpoints
- **Database queries:** Optimized with indexes

---

## Integration Examples

### Slack Webhook Integration

```python
import requests

def send_alert_to_slack(webhook_url, feature, risk_level):
    message = {
        "text": f"🚨 QA Alert",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{feature}* - {risk_level} Risk"
                }
            }
        ]
    }
    requests.post(webhook_url, json=message)

# Usage
send_alert_to_slack(
    "https://hooks.slack.com/services/...",
    "DraftJob",
    "Critical"
)
```

### GitHub Issue Creation

```python
import requests

def create_github_issue(repo, token, title, body):
    headers = {"Authorization": f"token {token}"}
    data = {"title": title, "body": body}
    requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        json=data,
        headers=headers
    )
```

---

## Testing Tools

### Postman Collection

Create a Postman collection with all endpoints for easy testing.

### cURL Batch Script

```bash
#!/bin/bash

# Test all endpoints
echo "Testing QA Analytics API..."

# Health
curl -s http://localhost:5000/api/health | jq .

# Summary
curl -s http://localhost:5000/api/summary | jq .summary

# Forecasts
curl -s http://localhost:5000/api/forecast/DraftJob | jq .

# Anomalies
curl -s http://localhost:5000/api/anomalies | jq .
```

---

## Support

For issues or questions:
1. Check the [README.md](README.md)
2. Review this guide
3. Check API logs: `docker-compose logs backend`
4. Submit an issue on GitHub

---

**Happy Testing! 🚀**
