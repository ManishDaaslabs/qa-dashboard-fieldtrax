# QA Analytics Platform 2026
## Enterprise-Grade AI-Powered Predictive Analytics for Test Execution

![Version](https://img.shields.io/badge/version-2.0.0-blue) ![Python](https://img.shields.io/badge/python-3.11%2B-green) ![License](https://img.shields.io/badge/license-MIT-blue)

---

## 🎯 Overview

A **production-grade Python application** combining:
- **Real-time test execution monitoring**
- **AI-powered predictive analytics** (forecasting, anomaly detection, root cause analysis)
- **Live dashboard** with modern interactive UI
- **Enterprise architecture** ready for deployment
- **CSV/Excel data ingestion**

### Key Features

✅ **Predictive Forecasting** - 7-day pass rate predictions with confidence scores  
✅ **Anomaly Detection** - Identify unusual test failures automatically  
✅ **Root Cause Analysis** - Understand why tests are failing with ML insights  
✅ **Risk Prediction** - Identify high-risk features before they fail  
✅ **Live Monitoring** - Real-time dashboard with auto-refresh  
✅ **Scalable Architecture** - Docker, PostgreSQL, Nginx, REST API  
✅ **Enterprise UI** - Modern React dashboard with Recharts visualizations  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│           Frontend (React)                          │
│  ├─ Overview Dashboard                             │
│  ├─ Forecast Trends                                │
│  ├─ Anomaly Detection UI                           │
│  └─ Risk Assessment Panel                          │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP/REST API
┌──────────────────▼──────────────────────────────────┐
│      Backend (Flask + SQLAlchemy)                   │
│  ├─ Analytics Engine (ML Models)                   │
│  ├─ REST API Endpoints                             │
│  ├─ Data Ingestion Pipeline                        │
│  └─ Database ORM Layer                             │
└──────────────────┬──────────────────────────────────┘
                   │
    ┌──────────────┴──────────────┐
    │                             │
┌───▼────────────┐    ┌──────────▼──────┐
│  PostgreSQL    │    │  SQLite (Dev)   │
│  (Production)  │    │  (Development)  │
└────────────────┘    └─────────────────┘
```

### Tech Stack

**Backend:**
- Flask 3.0 - REST API framework
- SQLAlchemy - ORM
- Pandas - Data processing
- Scikit-learn - ML models
- Statsmodels - Time series forecasting
- PostgreSQL - Production database

**Frontend:**
- React 18 - UI framework
- Recharts - Data visualizations
- Axios - HTTP client
- CSS-in-JS - Styling

**DevOps:**
- Docker - Containerization
- Docker Compose - Multi-container orchestration
- Nginx - Reverse proxy
- Gunicorn - WSGI server

---

## 🚀 Quick Start

### Option 1: Local Development (Recommended for first-time setup)

**Requirements:**
- Python 3.11+
- pip
- 2GB free disk space

**Setup:**

```bash
# 1. Clone/download the project
cd qa_analytics_platform

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()

# 5. Run the application
python app.py
```

Backend starts at: **http://localhost:5000**

**Test the API:**
```bash
# Health check
curl http://localhost:5000/api/health

# Get dashboard summary
curl http://localhost:5000/api/summary

# Upload test data
curl -X POST -F "file=@test_report.xlsx" http://localhost:5000/api/upload
```

---

### Option 2: Docker (Production-Ready)

**Requirements:**
- Docker Desktop
- 4GB free disk space

**Setup:**

```bash
# 1. Build and start containers
docker-compose up -d

# 2. Check logs
docker-compose logs -f backend

# 3. Verify services
curl http://localhost:5000/api/health
curl http://localhost:80/api/health
```

**Services:**
- Backend API: http://localhost:5000
- Nginx Proxy: http://localhost:80
- PostgreSQL: localhost:5432

**Useful commands:**
```bash
# Stop all services
docker-compose down

# View logs
docker-compose logs backend

# Execute command in container
docker-compose exec backend python -c "from app import db; db.create_all()"

# Restart a service
docker-compose restart backend
```

---

## 📊 API Reference

### Core Endpoints

#### `/api/health`
Health check endpoint.
```bash
GET /api/health
Response: { "status": "healthy", "timestamp": "...", "version": "2.0.0" }
```

#### `/api/upload`
Upload CSV/Excel test execution reports.
```bash
POST /api/upload
Body: multipart/form-data with 'file' field
Response: { "status": "success", "records_inserted": 42 }
```

**Supported columns in CSV/Excel:**
- FEATURE (string)
- TOTAL TESTS (integer)
- PASSED (integer)
- FAILED (integer)
- PENDING (integer)
- PASS RATE % (float)
- DEFECTS (integer)
- RISK LEVEL (string: Critical/High/Low)

#### `/api/summary`
Overall dashboard summary.
```bash
GET /api/summary
Response: {
  "summary": {
    "total_tests": 427,
    "passed": 202,
    "failed": 49,
    "pending": 176,
    "pass_rate": 47.3,
    "health_score": 27.3,
    "critical_features": 3,
    "high_risk_features": 5,
    "total_defects": 10
  },
  "features": { "DraftJob": "High", "BranchOverhead": "High", ... }
}
```

#### `/api/tests`
Get test executions with filtering.
```bash
GET /api/tests?feature=DraftJob&days=30
Response: { "total": 15, "data": [...] }
```

#### `/api/forecast/<feature_name>`
7-day pass rate forecast.
```bash
GET /api/forecast/DraftJob?days=7
Response: {
  "feature": "DraftJob",
  "forecast": [
    { "date": "2026-09-05", "predicted_pass_rate": 94.2, "confidence": 0.87 },
    ...
  ],
  "trend": "improving",
  "average_forecast": 93.8
}
```

#### `/api/anomalies`
Detect anomalies in test execution.
```bash
GET /api/anomalies?days=30
Response: {
  "total_anomalies": 2,
  "anomalies": [
    {
      "feature": "Break_Types_and_No_Show",
      "date": "2026-09-02",
      "anomaly_score": -0.45,
      "reason": "Unusual pattern detected - Pass rate: 30.2%, Failed tests: 8",
      "severity": "High"
    },
    ...
  ]
}
```

#### `/api/risk/<feature_name>`
Risk prediction for a feature.
```bash
GET /api/risk/DraftJob
Response: {
  "feature": "DraftJob",
  "risk_score": 0.35,
  "risk_level": "High",
  "pass_rate": 93.0,
  "recommendations": [
    "High failure rate detected. Review test design and environment."
  ]
}
```

#### `/api/rootcause/<feature_name>`
Root cause analysis.
```bash
GET /api/rootcause/DraftJob?days=30
Response: {
  "feature": "DraftJob",
  "period_days": 30,
  "total_executions": 12,
  "average_pass_rate": 92.1,
  "average_failures": 4.7,
  "failure_trend": "decreasing",
  "variance_in_failures": 1.2,
  "insights": [...]
}
```

#### `/api/dashboard`
Complete dashboard data (all metrics in one call).
```bash
GET /api/dashboard?days=30
Response: {
  "summary": {...},
  "features": {...},
  "executions": [...],
  "anomalies": [...],
  "forecasts": {...},
  "timestamp": "..."
}
```

---

## 📈 ML Models & Analytics

### 1. **Forecasting Model**
- **Algorithm:** Linear Regression with confidence intervals
- **Input:** Historical pass rates + execution dates
- **Output:** 7-day ahead predictions with confidence scores
- **Use Case:** Plan resource allocation, identify trends

### 2. **Anomaly Detection**
- **Algorithm:** Isolation Forest
- **Features:** Pass rate, failed tests count
- **Output:** Anomaly score, severity classification
- **Use Case:** Alert on unusual test failures

### 3. **Risk Prediction**
- **Algorithm:** Multi-factor scoring (pass rate + failures + defects)
- **Scoring:** 0-1 risk scale → Critical/High/Low
- **Output:** Risk level, actionable recommendations
- **Use Case:** Prioritize features for focus/debugging

### 4. **Root Cause Analysis**
- **Algorithm:** Correlation analysis + statistical summary
- **Metrics:** Failure trends, variance, correlations
- **Output:** Insights and patterns
- **Use Case:** Understand WHY tests are failing

---

## 📝 Sample Data

The platform comes with FieldTrax QA data from your project:

| Feature | Total | Passed | Failed | Pass Rate | Risk |
|---------|-------|--------|--------|-----------|------|
| DraftJob | 57 | 53 | 4 | 93.0% | High |
| BranchOverhead | 18 | 15 | 3 | 83.3% | High |
| Break_Types_and_No_Show | 43 | 13 | 8 | 30.2% | Critical |
| Recall_a_dispatch | 39 | 28 | 11 | 71.8% | Critical |
| ProjectGroupings | 189 | 39 | 8 | 20.6% | Critical |
| Warehouse_Overhead | 17 | 9 | 2 | 52.9% | High |
| ReadyToWork | 26 | 14 | 10 | 53.8% | Critical |
| TaskGrouping | 38 | 31 | 3 | 81.6% | High |

**Total:** 427 tests, 47.3% pass rate, 10 defects, 3 critical features

---

## 🔧 Configuration

### Environment Variables

Create `.env` file (development only):

```env
# Database
DATABASE_URL=postgresql://qa_admin:password@localhost:5432/qa_analytics

# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# API
API_PORT=5000
API_HOST=0.0.0.0

# File uploads
MAX_CONTENT_LENGTH=52428800  # 50MB
UPLOAD_FOLDER=/tmp/qa_uploads
```

### Database Configuration

**Development (SQLite):**
- Uses SQLite by default
- File: `qa_analytics.db`
- No setup needed

**Production (PostgreSQL):**
```bash
# Using docker-compose (recommended)
docker-compose up -d postgres

# Or manually with psql:
psql -U postgres
CREATE DATABASE qa_analytics;
CREATE USER qa_admin WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE qa_analytics TO qa_admin;
```

---

## 📊 Frontend Setup

To run the React frontend standalone:

```bash
# 1. Install Node.js 18+
# 2. Create React app
npx create-react-app qa-analytics-frontend

# 3. Replace src/App.jsx with frontend.jsx
# 4. Install dependencies
npm install axios recharts

# 5. Start dev server
npm start
```

Frontend will be at: **http://localhost:3000**

---

## 🧪 Testing

### Manual API Testing

```bash
# 1. Upload sample data
curl -X POST -F "file=@DraftJob_Test_execution_report.xlsx" \
  http://localhost:5000/api/upload

# 2. Get summary
curl http://localhost:5000/api/summary | jq

# 3. Get forecast
curl http://localhost:5000/api/forecast/DraftJob | jq

# 4. Detect anomalies
curl http://localhost:5000/api/anomalies | jq

# 5. Get risk assessment
curl http://localhost:5000/api/risk/DraftJob | jq
```

### Python Testing

```python
import requests

BASE_URL = "http://localhost:5000/api"

# Get summary
resp = requests.get(f"{BASE_URL}/summary")
print(resp.json())

# Get forecast
resp = requests.get(f"{BASE_URL}/forecast/DraftJob")
print(resp.json())

# Upload file
with open("test_report.xlsx", "rb") as f:
    resp = requests.post(f"{BASE_URL}/upload", 
                        files={"file": f})
    print(resp.json())
```

---

## 🚀 Deployment

### AWS EC2 Deployment

```bash
# 1. SSH into EC2 instance
ssh -i key.pem ec2-user@your-instance

# 2. Install Docker & Docker Compose
sudo yum update -y
sudo yum install docker -y
sudo usermod -a -G docker ec2-user
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. Clone project
git clone <your-repo> qa_analytics
cd qa_analytics

# 4. Create .env with production settings
echo "DATABASE_URL=postgresql://qa_admin:STRONG_PASSWORD@postgres:5432/qa_analytics" > .env

# 5. Start services
docker-compose up -d

# 6. Configure security group
# Allow inbound: TCP 80, 443, 5000
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qa-analytics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: qa-analytics
  template:
    metadata:
      labels:
        app: qa-analytics
    spec:
      containers:
      - name: backend
        image: qa-analytics:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: qa-analytics-secrets
              key: database-url
```

---

## 📚 Documentation

- **API Docs:** See API Reference section above
- **Architecture:** See Architecture section above
- **ML Models:** See ML Models & Analytics section above
- **Deployment:** See Deployment section above

---

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000

# Kill process
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL is running
docker-compose ps

# Restart database
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Out of Memory
```bash
# Increase Docker memory in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

### File Upload Fails
```bash
# Check upload folder permissions
chmod 777 /tmp/qa_uploads

# Check file size
ls -lh upload_file.xlsx

# Max size is 50MB
```

---

## 📝 Development Roadmap

- [ ] Real-time WebSocket updates
- [ ] Advanced ML models (LSTM, Prophet)
- [ ] Slack/Teams integration
- [ ] Historical trend reports
- [ ] Export to PDF/Excel
- [ ] User authentication & RBAC
- [ ] Multi-tenant support
- [ ] Mobile app (React Native)
- [ ] GraphQL API
- [ ] Advanced data quality checks

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/my-feature`
5. Submit pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📞 Support

- **Issues:** GitHub Issues
- **Email:** support@daaslabs.ai
- **Documentation:** Full API docs in this README

---

**QA Analytics Platform 2026** | Built for Enterprise Testing at Scale
