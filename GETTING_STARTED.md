# 🚀 Getting Started with QA Analytics Platform 2026

Welcome to the enterprise-grade QA Analytics Platform! This guide will get you up and running in 5 minutes.

---

## ⚡ 30-Second Quick Start

### Option A: Local Development (Simplest)

```bash
cd qa_analytics_platform

# Linux/Mac
bash setup.sh dev

# Windows (use Git Bash or WSL)
bash setup.sh dev
```

Then:
```bash
source venv/bin/activate
python app.py
```

**API is now at:** http://localhost:5000/api/health

### Option B: Docker (Production)

```bash
cd qa_analytics_platform
bash setup.sh prod
```

**API is now at:** http://localhost:5000/api/health

---

## 📊 Upload Your First Test Data

### Using curl

```bash
curl -X POST \
  -F "file=@DraftJob_Test_execution_report.xlsx" \
  http://localhost:5000/api/upload
```

### Using Python

```python
import requests

with open("test_report.xlsx", "rb") as f:
    response = requests.post(
        "http://localhost:5000/api/upload",
        files={"file": f}
    )
    print(response.json())
```

### Expected Response

```json
{
  "status": "success",
  "message": "Successfully imported 42 records",
  "records_inserted": 42
}
```

---

## 📈 Get Your First Insights

### 1. Get Dashboard Summary

```bash
curl http://localhost:5000/api/summary | jq .summary
```

**Sample output:**
```json
{
  "total_tests": 427,
  "passed": 202,
  "failed": 49,
  "pending": 176,
  "pass_rate": 47.3,
  "health_score": 27.3,
  "critical_features": 3,
  "high_risk_features": 5,
  "total_defects": 10
}
```

### 2. Get AI Forecast

```bash
curl http://localhost:5000/api/forecast/DraftJob | jq .forecast
```

**Sample output:**
```json
[
  {
    "date": "2026-09-05T00:00:00",
    "predicted_pass_rate": 94.2,
    "confidence": 0.87
  }
]
```

### 3. Detect Anomalies

```bash
curl http://localhost:5000/api/anomalies | jq .anomalies
```

### 4. Get Risk Assessment

```bash
curl http://localhost:5000/api/risk/DraftJob | jq .
```

---

## 🎯 Key Features to Explore

### ✅ Real-Time Monitoring
- Live dashboard with auto-refresh
- Feature-by-feature test status
- Health score calculation

### 🔮 Predictive Analytics
- 7-day pass rate forecasts
- Trend analysis (improving/declining)
- Confidence scores for predictions

### 🚨 Anomaly Detection
- Identify unusual test failures
- Automatic severity classification
- Historical pattern analysis

### ⚠️ Risk Assessment
- Multi-factor risk scoring
- Actionable recommendations
- Critical feature alerts

### 🔍 Root Cause Analysis
- Understand failure patterns
- Correlation analysis
- Variance tracking

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Full documentation, architecture, deployment |
| [API_EXAMPLES.md](API_EXAMPLES.md) | Complete API reference with examples |
| This file | Quick start guide |

---

## 🔧 Command Reference

### Local Development

```bash
# Start the app
python app.py

# Run in virtual environment
source venv/bin/activate
python app.py

# Test API
curl http://localhost:5000/api/health

# Stop (Ctrl+C)
```

### Docker

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# Execute command
docker-compose exec backend python -c "print('Hello')"
```

---

## 📁 Project Structure

```
qa_analytics_platform/
├── app.py                    # Main Flask application
├── frontend.jsx              # React component
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker container definition
├── docker-compose.yml        # Multi-container orchestration
├── nginx.conf                # Reverse proxy config
├── setup.sh                  # Automated setup script
├── README.md                 # Full documentation
├── API_EXAMPLES.md           # API reference & examples
├── GETTING_STARTED.md        # This file
├── .env.example              # Environment variables template
└── qa_analytics.db           # SQLite database (created at runtime)
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>
```

### Database Connection Error

```bash
# Check if database exists
ls qa_analytics.db

# Delete and recreate
rm qa_analytics.db
python app.py  # Will create new database
```

### Import Errors

```bash
# Verify all dependencies installed
pip install -r requirements.txt

# Upgrade pip
pip install --upgrade pip
```

### Docker Issues

```bash
# Rebuild images
docker-compose build --no-cache

# Remove old containers
docker-compose down -v

# Start fresh
docker-compose up -d
```

---

## 💡 Next Steps

### 1. Upload Your Test Data
- Prepare your test execution report in Excel/CSV
- Ensure columns match: FEATURE, TOTAL TESTS, PASSED, FAILED, PENDING, PASS RATE %, DEFECTS, RISK LEVEL
- Upload via `/api/upload` endpoint

### 2. Explore the Dashboard
- Check summary: `/api/summary`
- View forecasts: `/api/forecast/<feature>`
- Review anomalies: `/api/anomalies`

### 3. Set Up Frontend
- Copy `frontend.jsx` to your React app
- Install dependencies: `npm install axios recharts`
- Update API_BASE URL to point to your backend

### 4. Deploy to Production
- See [README.md](README.md) for EC2/Kubernetes deployment
- Use Docker Compose for easiest setup
- Configure PostgreSQL for production

### 5. Integrate with Your Tools
- Slack webhooks for alerts
- GitHub issues for defects
- Email notifications
- JIRA integration

---

## 📊 Sample Data

The platform comes with FieldTrax QA data pre-loaded:

| Feature | Pass Rate | Risk | Status |
|---------|-----------|------|--------|
| DraftJob | 93.0% | High | Stable |
| BranchOverhead | 83.3% | High | Monitor |
| Break_Types_and_No_Show | 30.2% | Critical | Action Required |
| Recall_a_dispatch | 71.8% | Critical | Action Required |
| ProjectGroupings | 20.6% | Critical | Urgent |
| Warehouse_Overhead | 52.9% | High | Monitor |
| ReadyToWork | 53.8% | Critical | Action Required |
| TaskGrouping | 81.6% | High | Stable |

**Total: 427 tests, 47.3% pass rate, 10 defects**

---

## 🎓 Learning Path

### Beginner (15 minutes)
1. ✅ Install locally (`setup.sh dev`)
2. ✅ Upload test data
3. ✅ View dashboard summary

### Intermediate (1 hour)
1. ✅ Explore all API endpoints
2. ✅ Understand ML model outputs
3. ✅ Set up automated uploads

### Advanced (2 hours)
1. ✅ Deploy to Docker
2. ✅ Configure PostgreSQL
3. ✅ Set up integrations
4. ✅ Customize ML models

---

## 🤝 Community & Support

- **Documentation:** See [README.md](README.md) and [API_EXAMPLES.md](API_EXAMPLES.md)
- **Issues:** Check the troubleshooting section above
- **Feedback:** We'd love to hear from you!

---

## 🎉 You're Ready!

You now have a **production-grade AI-powered QA analytics platform** running locally!

### Try these right now:

```bash
# 1. Upload sample data
curl -X POST -F "file=@DraftJob_Test_execution_report.xlsx" \
  http://localhost:5000/api/upload

# 2. Get summary
curl http://localhost:5000/api/summary

# 3. Get forecast
curl http://localhost:5000/api/forecast/DraftJob

# 4. Detect anomalies
curl http://localhost:5000/api/anomalies

# 5. Get risk assessment
curl http://localhost:5000/api/risk/DraftJob

# 6. Root cause analysis
curl http://localhost:5000/api/rootcause/DraftJob
```

---

## 📞 Quick Reference

| Task | Command/URL |
|------|------------|
| Start app | `python app.py` |
| Check health | `curl http://localhost:5000/api/health` |
| Upload data | `curl -X POST -F "file=@report.xlsx" http://localhost:5000/api/upload` |
| Get summary | `curl http://localhost:5000/api/summary` |
| Get forecast | `curl http://localhost:5000/api/forecast/FeatureName` |
| View logs | `docker-compose logs -f backend` |
| Stop services | `docker-compose down` |

---

**Happy Analytics! 🚀**

For detailed information, see [README.md](README.md) and [API_EXAMPLES.md](API_EXAMPLES.md).
