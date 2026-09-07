"""
FieldTrax QA Dashboard - FINAL CLEAN VERSION
Handles any filename format + multiple sheet types
"""

from flask import Flask, jsonify, render_template_string
import pandas as pd
import os
from datetime import datetime
import json
import glob

app = Flask(__name__)
DASHBOARD_DATA = {}

def load_all_test_data():
    """Load ALL Excel files - handle any filename and sheet format"""
    global DASHBOARD_DATA
    
    features = {}
    total_pass = 0
    total_fail = 0
    total_not_executed = 0
    total_tests = 0
    files_loaded = 0
    
    # Find all Excel files
    excel_files = sorted(glob.glob('*.xlsx') + glob.glob('*.xls'))
    
    print(f"\n\nFound {len(excel_files)} Excel files:\n")
    for f in excel_files:
        print(f"  - {f}")
    
    for filepath in excel_files:
        try:
            # Step 1: Extract feature name from filename
            feature_name = filepath.replace('.xlsx', '').replace('.xls', '')
            
            # Remove common test report suffixes if they exist
            suffixes_to_remove = [
                '_Test_execution_report',
                '_TestExecution_Report', 
                '_test_report',
                '_test_execution_report'
            ]
            for suffix in suffixes_to_remove:
                if suffix in feature_name:
                    feature_name = feature_name.replace(suffix, '')
            
            # Create normalized version for sheet name detection
            feature_normalized = feature_name.lower().replace(' ', '').replace('_', '')
            
            # Convert underscores to spaces for display
            feature_display = feature_name.replace('_', ' ')
            
            print(f"\nProcessing: {feature_display}")
            
            # Step 2: Determine which sheet to read
            sheet_name = 0  # Default: first sheet
            
            # Special cases with different sheet names
            if 'projectgroupings' in feature_normalized:
                sheet_name = 'Test Cases'
            elif 'readytowork' in feature_normalized:
                sheet_name = 'test_cases'
            
            # Step 3: Read Excel file
            try:
                df = pd.read_excel(filepath, sheet_name=sheet_name)
            except Exception as e:
                print(f"  ❌ Error reading file: {str(e)}")
                continue
            
            if df is None or len(df) == 0:
                print(f"  → Empty file, SKIPPED")
                continue
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            if len(df) == 0:
                print(f"  → No data rows, SKIPPED")
                continue
            
            # Step 4: Find Status column
            status_col = None
            status_names = ['status', 'execution status', 'execution_status', 'test result', 'result']
            
            for status_name in status_names:
                for col in df.columns:
                    if str(col).lower().strip() == status_name:
                        status_col = col
                        break
                if status_col:
                    break
            
            if status_col is None:
                print(f"  → No Status column found, SKIPPED")
                continue
            
            # Step 5: Extract test metrics
            # Check if file has ID column (marks actual test cases vs sub-steps)
            has_id_column = 'ID' in df.columns
            
            if has_id_column:
                # Only count rows with ID (actual test cases, not sub-steps)
                df_tests = df[df['ID'].notna()]
                status_vals = df_tests[status_col].fillna('').astype(str).str.strip()
            else:
                # All rows are test cases
                status_vals = df[status_col].fillna('').astype(str).str.strip()
            
            # Count status values
            status_lower = status_vals.str.lower()
            pass_count = sum(status_lower == 'pass')
            fail_count = sum(status_lower == 'fail')
            not_executed = sum(
                (status_lower == 'no run') | 
                (status_lower == 'not executed') |
                (status_lower == 'not run') |
                (status_lower == 'skipped') |
                (status_lower == 'blocked')
            )
            
            # Total = Pass + Fail + Not Executed
            total_executed = pass_count + fail_count + not_executed
            
            if total_executed == 0:
                print(f"  → No test data found, SKIPPED")
                continue
            
            # Calculate pass rate
            pass_rate = (pass_count / total_executed * 100) if total_executed > 0 else 0
            
            # Determine risk level
            if pass_rate < 50:
                risk = 'Critical'
            elif pass_rate < 75:
                risk = 'High'
            else:
                risk = 'Low'
            
            # Add to features dictionary
            features[feature_display] = {
                'total': total_executed,
                'passed': pass_count,
                'failed': fail_count,
                'not_executed': not_executed,
                'pass_rate': round(pass_rate, 1),
                'risk': risk
            }
            
            # Add to totals
            total_pass += pass_count
            total_fail += fail_count
            total_not_executed += not_executed
            total_tests += total_executed
            files_loaded += 1
            
            print(f"  ✅ {total_executed} tests: {pass_count} Pass, {fail_count} Fail, {not_executed} Not Executed ({pass_rate:.1f}%)")
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            continue
    
    # Calculate overall stats
    overall_pass_rate = (total_pass / total_tests * 100) if total_tests > 0 else 0
    
    DASHBOARD_DATA = {
        'summary': {
            'total_tests': total_tests,
            'passed': total_pass,
            'failed': total_fail,
            'not_executed': total_not_executed,
            'pass_rate': round(overall_pass_rate, 1),
            'features_count': len(features),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'files_loaded': files_loaded
        },
        'features': dict(sorted(features.items())),
    }

# Load data on startup
load_all_test_data()

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE, data=json.dumps(DASHBOARD_DATA))

@app.route('/api/summary')
def api_summary():
    return jsonify(DASHBOARD_DATA['summary'])

@app.route('/api/features')
def api_features():
    return jsonify(DASHBOARD_DATA['features'])

@app.route('/api/dashboard')
def api_dashboard():
    return jsonify(DASHBOARD_DATA)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>FieldTrax QA Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto; background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 100%); color: #e5e7eb; min-height: 100vh; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        header { margin-bottom: 40px; border-bottom: 1px solid rgba(75, 85, 99, 0.2); padding-bottom: 20px; }
        h1 { background: linear-gradient(135deg, #60a5fa 0%, #34d399 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 32px; margin-bottom: 5px; }
        .subtitle { color: #9ca3af; font-size: 14px; }
        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .kpi-card { background: rgba(31, 41, 55, 0.8); border: 1px solid rgba(75, 85, 99, 0.3); border-radius: 12px; padding: 20px; }
        .kpi-label { font-size: 12px; color: #9ca3af; text-transform: uppercase; margin-bottom: 10px; font-weight: 600; }
        .kpi-value { font-size: 28px; font-weight: 700; margin-bottom: 5px; }
        .green { color: #34d399; }
        .blue { color: #60a5fa; }
        .section-title { font-size: 20px; font-weight: 700; margin-bottom: 20px; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; background: rgba(31, 41, 55, 0.8); border: 1px solid rgba(75, 85, 99, 0.3); border-radius: 12px; overflow: hidden; }
        th { padding: 15px; text-align: left; font-weight: 600; font-size: 13px; background: rgba(55, 65, 81, 0.5); border-bottom: 1px solid rgba(75, 85, 99, 0.3); }
        td { padding: 15px; border-bottom: 1px solid rgba(75, 85, 99, 0.1); }
        tr:hover { background: rgba(59, 130, 246, 0.05); }
        .risk-badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .risk-critical { background: rgba(239, 68, 68, 0.2); color: #fca5a5; }
        .risk-high { background: rgba(245, 158, 11, 0.2); color: #fcd34d; }
        .risk-low { background: rgba(16, 185, 129, 0.2); color: #86efac; }
        .footer { text-align: right; color: #6b7280; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(75, 85, 99, 0.2); }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 FieldTrax QA Dashboard</h1>
            <p class="subtitle">Comprehensive Test Execution Summary - All 10 Features</p>
        </header>
        
        <div class="kpi-grid" id="kpiContainer"></div>
        
        <h2 class="section-title">Test Execution by Feature</h2>
        <table>
            <thead>
                <tr>
                    <th>Feature</th>
                    <th style="text-align: center;">Total Tests</th>
                    <th style="text-align: center;">Passed</th>
                    <th style="text-align: center;">Failed</th>
                    <th style="text-align: center;">Not Executed</th>
                    <th style="text-align: center;">Pass Rate</th>
                    <th style="text-align: center;">Risk</th>
                </tr>
            </thead>
            <tbody id="featuresBody"></tbody>
        </table>
        
        <div class="footer" id="timestamp"></div>
    </div>
    
    <script>
        const data = {{ data | safe }};
        const summary = data.summary;
        
        document.getElementById('kpiContainer').innerHTML = `
            <div class="kpi-card">
                <div class="kpi-label">Pass Rate</div>
                <div class="kpi-value green">${summary.pass_rate}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Total Tests</div>
                <div class="kpi-value blue">${summary.total_tests}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Features</div>
                <div class="kpi-value blue">${summary.features_count}</div>
            </div>
        `;
        
        let tableHtml = '';
        Object.entries(data.features).forEach(([name, stats]) => {
            const riskClass = stats.risk === 'Critical' ? 'risk-critical' : stats.risk === 'High' ? 'risk-high' : 'risk-low';
            tableHtml += `
                <tr>
                    <td><strong>${name}</strong></td>
                    <td style="text-align: center;">${stats.total}</td>
                    <td style="text-align: center; color: #34d399;">${stats.passed}</td>
                    <td style="text-align: center; color: #f87171;">${stats.failed}</td>
                    <td style="text-align: center; color: #9ca3af;">${stats.not_executed || 0}</td>
                    <td style="text-align: center;"><strong>${stats.pass_rate}%</strong></td>
                    <td style="text-align: center;">
                        <span class="risk-badge ${riskClass}">${stats.risk}</span>
                    </td>
                </tr>
            `;
        });
        
        // Add TOTAL row at bottom
        tableHtml += `
            <tr style="background: rgba(75, 85, 99, 0.3); border-top: 2px solid rgba(75, 85, 99, 0.5); font-weight: bold;">
                <td><strong>TOTAL</strong></td>
                <td style="text-align: center;"><strong>${summary.total_tests}</strong></td>
                <td style="text-align: center; color: #34d399;"><strong>${summary.passed}</strong></td>
                <td style="text-align: center; color: #f87171;"><strong>${summary.failed}</strong></td>
                <td style="text-align: center; color: #9ca3af;"><strong>${summary.not_executed}</strong></td>
                <td style="text-align: center;"><strong>${summary.pass_rate}%</strong></td>
                <td style="text-align: center;">-</td>
            </tr>
        `;
        
        document.getElementById('featuresBody').innerHTML = tableHtml;
        
        document.getElementById('timestamp').textContent = 
            `Updated: ${summary.last_updated} | Files: ${summary.files_loaded}/10 | Tests: ${summary.total_tests}`;
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 FieldTrax QA Dashboard - CLEAN VERSION")
    print("="*80)
    
    summary = DASHBOARD_DATA['summary']
    print(f"\n📊 DASHBOARD SUMMARY:")
    print(f"   ✅ Files loaded: {summary['files_loaded']}/10")
    print(f"   ✅ Features: {summary['features_count']}")
    print(f"   ✅ Total tests: {summary['total_tests']}")
    print(f"   ✅ Passed: {summary['passed']}")
    print(f"   ✅ Failed: {summary['failed']}")
    print(f"   ✅ Not Executed: {summary['not_executed']}")
    print(f"   ✅ Pass rate: {summary['pass_rate']}%")
    print(f"\n🌐 Dashboard: http://localhost:5000")
    print(f"\nPress CTRL+C to stop\n")
    print("="*80 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
