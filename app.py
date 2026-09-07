"""
QA Analytics Platform - Enterprise-Grade Backend
AI-Powered Predictive Analytics for Test Execution
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import io
from werkzeug.utils import secure_filename

# ML & Analytics imports
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from scipy import stats
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///qa_analytics.db')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# ============ DATABASE MODELS ============

class TestExecution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feature_name = db.Column(db.String(255), nullable=False)
    total_tests = db.Column(db.Integer, nullable=False)
    passed = db.Column(db.Integer, nullable=False)
    failed = db.Column(db.Integer, nullable=False)
    pending = db.Column(db.Integer, nullable=False)
    pass_rate = db.Column(db.Float, nullable=False)
    execution_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    defects_count = db.Column(db.Integer, default=0)
    risk_level = db.Column(db.String(50), default='High')
    
    def to_dict(self):
        return {
            'id': self.id,
            'feature_name': self.feature_name,
            'total_tests': self.total_tests,
            'passed': self.passed,
            'failed': self.failed,
            'pending': self.pending,
            'pass_rate': round(self.pass_rate, 2),
            'execution_date': self.execution_date.isoformat(),
            'defects_count': self.defects_count,
            'risk_level': self.risk_level
        }

class Defect(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    defect_id = db.Column(db.String(50), unique=True, nullable=False)
    severity = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    summary = db.Column(db.String(500), nullable=False)
    feature = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='New')
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'defect_id': self.defect_id,
            'severity': self.severity,
            'priority': self.priority,
            'summary': self.summary,
            'feature': self.feature,
            'status': self.status,
            'created_date': self.created_date.isoformat()
        }

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feature_name = db.Column(db.String(255), nullable=False)
    prediction_type = db.Column(db.String(50), nullable=False)  # forecast, anomaly, risk
    prediction_value = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow)
    predicted_for_date = db.Column(db.DateTime, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'feature_name': self.feature_name,
            'prediction_type': self.prediction_type,
            'prediction_value': round(self.prediction_value, 2),
            'confidence': round(self.confidence, 2),
            'prediction_date': self.prediction_date.isoformat(),
            'predicted_for_date': self.predicted_for_date.isoformat()
        }

# ============ ML MODELS & ANALYTICS ============

class QAAnalyticsEngine:
    """Advanced ML-powered QA Analytics Engine"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.forecaster = LinearRegression()
    
    @staticmethod
    def calculate_statistics(data):
        """Calculate comprehensive statistics"""
        return {
            'mean': float(np.mean(data)),
            'median': float(np.median(data)),
            'std_dev': float(np.std(data)),
            'min': float(np.min(data)),
            'max': float(np.max(data)),
            'q1': float(np.percentile(data, 25)),
            'q3': float(np.percentile(data, 75))
        }
    
    def detect_anomalies(self, test_executions):
        """Anomaly Detection - Identify unusual test failures"""
        if len(test_executions) < 5:
            return []
        
        df = pd.DataFrame([t.to_dict() for t in test_executions])
        features = df[['pass_rate', 'failed']].values
        
        # Normalize features
        features_scaled = self.scaler.fit_transform(features)
        
        # Detect anomalies
        anomalies = self.anomaly_detector.fit_predict(features_scaled)
        
        results = []
        for idx, (test, anomaly) in enumerate(zip(test_executions, anomalies)):
            if anomaly == -1:
                results.append({
                    'feature': test.feature_name,
                    'date': test.execution_date.isoformat(),
                    'anomaly_score': round(float(self.anomaly_detector.score_samples(features_scaled[idx:idx+1])[0]), 3),
                    'reason': f"Unusual pattern detected - Pass rate: {test.pass_rate}%, Failed tests: {test.failed}",
                    'severity': 'High' if test.pass_rate < 50 else 'Medium'
                })
        
        return results
    
    def forecast_pass_rate(self, feature_name, days_ahead=7):
        """Time Series Forecasting - Predict future pass rates"""
        executions = TestExecution.query.filter_by(feature_name=feature_name)\
            .order_by(TestExecution.execution_date).all()
        
        if len(executions) < 3:
            return {'error': 'Insufficient historical data'}
        
        df = pd.DataFrame([e.to_dict() for e in executions])
        df['days_since_start'] = (pd.to_datetime(df['execution_date']) - 
                                  pd.to_datetime(df['execution_date'].min())).dt.days
        
        X = df[['days_since_start']].values
        y = df['pass_rate'].values
        
        # Train model
        self.forecaster.fit(X, y)
        
        # Generate forecasts
        future_days = np.array([[len(X) + i] for i in range(days_ahead)])
        predictions = self.forecaster.predict(future_days)
        
        # Calculate confidence based on historical variance
        residuals = y - self.forecaster.predict(X)
        std_residuals = np.std(residuals)
        confidence = max(0, 1 - (std_residuals / 100))
        
        forecast_dates = [(datetime.utcnow() + timedelta(days=i)).isoformat() 
                         for i in range(1, days_ahead + 1)]
        
        return {
            'feature': feature_name,
            'forecast': [
                {
                    'date': date,
                    'predicted_pass_rate': round(float(pred), 1),
                    'confidence': round(confidence, 2)
                }
                for date, pred in zip(forecast_dates, predictions)
            ],
            'trend': 'improving' if predictions[-1] > predictions[0] else 'declining',
            'average_forecast': round(float(np.mean(predictions)), 1)
        }
    
    def risk_prediction(self, test_execution):
        """Risk Prediction - Identify high-risk features"""
        pass_rate = test_execution.pass_rate
        failed_ratio = test_execution.failed / max(test_execution.total_tests, 1)
        
        # Risk scoring algorithm
        risk_score = (
            (1 - pass_rate/100) * 0.4 +  # Pass rate weight
            failed_ratio * 0.3 +           # Failure ratio weight
            (test_execution.defects_count / max(test_execution.total_tests/10, 1)) * 0.3
        )
        
        if risk_score > 0.6:
            risk_level = 'Critical'
        elif risk_score > 0.4:
            risk_level = 'High'
        else:
            risk_level = 'Low'
        
        # Recommendations
        recommendations = []
        if pass_rate < 50:
            recommendations.append('Urgent: Pass rate below 50%. Conduct root cause analysis.')
        if failed_ratio > 0.3:
            recommendations.append('High failure rate detected. Review test design and environment.')
        if test_execution.defects_count > 5:
            recommendations.append('Multiple defects detected. Prioritize defect resolution.')
        
        return {
            'feature': test_execution.feature_name,
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'pass_rate': test_execution.pass_rate,
            'recommendations': recommendations
        }
    
    def root_cause_analysis(self, feature_name, lookback_days=30):
        """Root Cause Analysis - Identify why tests are failing"""
        cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
        executions = TestExecution.query.filter(
            TestExecution.feature_name == feature_name,
            TestExecution.execution_date >= cutoff_date
        ).order_by(TestExecution.execution_date).all()
        
        if not executions:
            return {'error': 'No data available'}
        
        df = pd.DataFrame([e.to_dict() for e in executions])
        
        # Calculate correlations
        analysis = {
            'feature': feature_name,
            'period_days': lookback_days,
            'total_executions': len(executions),
            'average_pass_rate': round(float(df['pass_rate'].mean()), 1),
            'average_failures': round(float(df['failed'].mean()), 1),
            'failure_trend': 'increasing' if df['failed'].iloc[-1] > df['failed'].iloc[0] else 'decreasing',
            'variance_in_failures': round(float(df['failed'].std()), 2),
            'correlation_failures_to_pending': round(float(df['failed'].corr(df['pending'])), 2),
            'insights': []
        }
        
        # Generate insights
        if df['failed'].std() > df['failed'].mean():
            analysis['insights'].append('High variance in test failures - unstable test environment')
        if df['pass_rate'].iloc[-1] < df['pass_rate'].iloc[0]:
            analysis['insights'].append('Pass rate declining over time - investigate recent changes')
        if df['pending'].mean() > df['total_tests'].mean() * 0.3:
            analysis['insights'].append('High number of pending tests - unblocking is critical')
        
        return analysis

# Initialize analytics engine
analytics = QAAnalyticsEngine()

# ============ API ENDPOINTS ============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0'
    })

@app.route('/api/upload', methods=['POST'])
def upload_data():
    """Upload CSV/Excel test data"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Parse file
        if filename.endswith('.xlsx'):
            df = pd.read_excel(filepath)
        elif filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        # Validate and insert data
        inserted = 0
        for _, row in df.iterrows():
            exec_data = TestExecution(
                feature_name=str(row.get('FEATURE', '')).strip(),
                total_tests=int(row.get('TOTAL TESTS', 0)),
                passed=int(row.get('PASSED', 0)),
                failed=int(row.get('FAILED', 0)),
                pending=int(row.get('PENDING', 0)),
                pass_rate=float(row.get('PASS RATE %', 0)) if isinstance(row.get('PASS RATE %', 0), (int, float)) else 0,
                defects_count=int(row.get('DEFECTS', 0)),
                risk_level=str(row.get('RISK LEVEL', 'High')).strip()
            )
            db.session.add(exec_data)
            inserted += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully imported {inserted} records',
            'records_inserted': inserted
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tests', methods=['GET'])
def get_test_executions():
    """Get all test executions with optional filtering"""
    feature = request.args.get('feature')
    days = request.args.get('days', default=30, type=int)
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    query = TestExecution.query.filter(TestExecution.execution_date >= cutoff_date)
    
    if feature:
        query = query.filter_by(feature_name=feature)
    
    executions = query.order_by(TestExecution.execution_date.desc()).all()
    
    return jsonify({
        'total': len(executions),
        'data': [e.to_dict() for e in executions]
    })

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get overall dashboard summary"""
    executions = TestExecution.query.order_by(TestExecution.execution_date.desc()).limit(100).all()
    
    if not executions:
        return jsonify({'error': 'No data available'}), 404
    
    total_tests = sum(e.total_tests for e in executions)
    total_passed = sum(e.passed for e in executions)
    total_failed = sum(e.failed for e in executions)
    total_pending = sum(e.pending for e in executions)
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    # Risk levels
    all_features = TestExecution.query.with_entities(TestExecution.feature_name).distinct().all()
    feature_risks = {}
    for feature_tuple in all_features:
        feature = feature_tuple[0]
        latest = TestExecution.query.filter_by(feature_name=feature).order_by(
            TestExecution.execution_date.desc()).first()
        if latest:
            feature_risks[feature] = latest.risk_level
    
    critical_count = sum(1 for r in feature_risks.values() if r == 'Critical')
    high_count = sum(1 for r in feature_risks.values() if r == 'High')
    
    return jsonify({
        'summary': {
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_failed,
            'pending': total_pending,
            'pass_rate': round(overall_pass_rate, 1),
            'health_score': round(max(0, overall_pass_rate - 20), 1),
            'critical_features': critical_count,
            'high_risk_features': high_count,
            'total_defects': sum(e.defects_count for e in executions),
            'last_updated': max(e.execution_date for e in executions).isoformat() if executions else None
        },
        'features': feature_risks
    })

@app.route('/api/forecast/<feature_name>', methods=['GET'])
def forecast_feature(feature_name):
    """Get 7-day pass rate forecast"""
    days = request.args.get('days', default=7, type=int)
    result = analytics.forecast_pass_rate(feature_name, days_ahead=days)
    return jsonify(result)

@app.route('/api/anomalies', methods=['GET'])
def detect_anomalies():
    """Detect anomalies in test execution"""
    days = request.args.get('days', default=30, type=int)
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    executions = TestExecution.query.filter(
        TestExecution.execution_date >= cutoff_date
    ).order_by(TestExecution.execution_date).all()
    
    anomalies = analytics.detect_anomalies(executions)
    
    return jsonify({
        'total_anomalies': len(anomalies),
        'period_days': days,
        'anomalies': anomalies
    })

@app.route('/api/risk/<feature_name>', methods=['GET'])
def get_risk_assessment(feature_name):
    """Get risk prediction for a feature"""
    latest = TestExecution.query.filter_by(feature_name=feature_name).order_by(
        TestExecution.execution_date.desc()).first()
    
    if not latest:
        return jsonify({'error': 'Feature not found'}), 404
    
    risk_analysis = analytics.risk_prediction(latest)
    return jsonify(risk_analysis)

@app.route('/api/rootcause/<feature_name>', methods=['GET'])
def root_cause(feature_name):
    """Root cause analysis for feature"""
    days = request.args.get('days', default=30, type=int)
    analysis = analytics.root_cause_analysis(feature_name, lookback_days=days)
    return jsonify(analysis)

@app.route('/api/defects', methods=['GET'])
def get_defects():
    """Get all defects"""
    feature = request.args.get('feature')
    severity = request.args.get('severity')
    
    query = Defect.query
    
    if feature:
        query = query.filter_by(feature=feature)
    if severity:
        query = query.filter_by(severity=severity)
    
    defects = query.all()
    return jsonify({
        'total': len(defects),
        'data': [d.to_dict() for d in defects]
    })

@app.route('/api/dashboard', methods=['GET'])
def get_full_dashboard():
    """Get complete dashboard data"""
    days = request.args.get('days', default=30, type=int)
    
    # Get summary
    summary_resp = get_summary()
    summary_data = summary_resp.get_json()
    
    # Get recent executions
    cutoff = datetime.utcnow() - timedelta(days=days)
    executions = TestExecution.query.filter(
        TestExecution.execution_date >= cutoff
    ).order_by(TestExecution.execution_date).all()
    
    # Get anomalies
    anomalies = analytics.detect_anomalies(executions)
    
    # Get forecasts for top features
    top_features = TestExecution.query.with_entities(
        TestExecution.feature_name,
        db.func.count(TestExecution.id).label('count')
    ).group_by(TestExecution.feature_name).order_by(
        db.func.count(TestExecution.id).desc()).limit(5).all()
    
    forecasts = {}
    for feature_tuple in top_features:
        feature = feature_tuple[0]
        forecast = analytics.forecast_pass_rate(feature, days_ahead=7)
        if 'error' not in forecast:
            forecasts[feature] = forecast
    
    return jsonify({
        'summary': summary_data['summary'],
        'features': summary_data['features'],
        'executions': [e.to_dict() for e in executions[-20:]],  # Last 20
        'anomalies': anomalies,
        'forecasts': forecasts,
        'timestamp': datetime.utcnow().isoformat()
    })

# ============ DATABASE INITIALIZATION ============

@app.before_request
def init_db():
    """Initialize database on first request"""
    db.create_all()

# ============ MAIN ============

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
