"""
FieldTrax QA Dashboard - No Pandas Version
Uses openpyxl only - works perfectly on Render!
"""

from flask import Flask, jsonify, render_template_string
from openpyxl import load_workbook
import os
from datetime import datetime
import json
import glob
import re

app = Flask(__name__)
DASHBOARD_DATA = {}

def normalize_severity(value):
    """Map many different severity spellings to Critical/High/Medium/Low"""
    if value is None:
        return None
    text = str(value).lower()
    if 'critical' in text:
        return 'Critical'
    if 'high' in text or 'major' in text:
        return 'High'
    if 'medium' in text or 'moderate' in text:
        return 'Medium'
    if 'low' in text or 'minor' in text:
        return 'Low'
    return None

def normalize_priority(value):
    """Map priority values like 'P1', '1', 'Priority P2' to P1/P2/P3"""
    if value is None:
        return None
    match = re.search(r'P?\s*([0-3])', str(value), re.IGNORECASE)
    if match:
        return 'P' + match.group(1)
    return None

def blank_bug_counts():
    return {
        'total': 0,
        'severity': {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0},
        'priority': {'P1': 0, 'P2': 0, 'P3': 0}
    }

def parse_bug_sheet(ws):
    """Parse a defects/bugs worksheet. Handles both normal column tables
    (Severity/Priority as headers) and the 'card style' layout used by
    one of the reports, where each bug is a small block of rows starting
    with a BUG-## / DEF-## id."""
    result = blank_bug_counts()
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return result

    header = [str(c).strip().lower() if c else '' for c in rows[0]]

    if 'severity' in header:
        sev_idx = header.index('severity')
        pri_idx = header.index('priority') if 'priority' in header else None
        id_idx = None
        for candidate in ('bug id', 'defect id'):
            if candidate in header:
                id_idx = header.index(candidate)
                break

        for row in rows[1:]:
            if not any(row):
                continue
            if id_idx is not None and (id_idx >= len(row) or not row[id_idx]):
                continue
            sev = normalize_severity(row[sev_idx]) if sev_idx < len(row) else None
            pri = normalize_priority(row[pri_idx]) if pri_idx is not None and pri_idx < len(row) else None
            result['total'] += 1
            if sev in result['severity']:
                result['severity'][sev] += 1
            if pri in result['priority']:
                result['priority'][pri] += 1
    else:
        for i, row in enumerate(rows):
            first = row[0] if row else None
            if first and isinstance(first, str) and re.match(r'^(BUG|DEF)[-_]?\d+', first.strip(), re.IGNORECASE):
                next_row = rows[i + 1] if i + 1 < len(rows) else None
                sev = normalize_severity(next_row[0]) if next_row else None
                pri = normalize_priority(next_row[1]) if next_row and len(next_row) > 1 else None
                result['total'] += 1
                if sev in result['severity']:
                    result['severity'][sev] += 1
                if pri in result['priority']:
                    result['priority'][pri] += 1

    return result

def load_all_test_data():
    """Load ALL Excel files using openpyxl only"""
    global DASHBOARD_DATA

    features = {}
    total_pass = 0
    total_fail = 0
    total_not_executed = 0
    total_tests = 0
    files_loaded = 0
    bug_summary = blank_bug_counts()
    
    # Find all Excel files
    excel_files = sorted(glob.glob('*.xlsx') + glob.glob('*.xls'))
    
    print(f"\n\nFound {len(excel_files)} Excel files:\n")
    for f in excel_files:
        print(f"  - {f}")
    
    for filepath in excel_files:
        try:
            # Extract feature name
            feature_name = filepath.replace('.xlsx', '').replace('.xls', '')
            
            # Remove common suffixes
            suffixes = ['_Test_execution_report', '_TestExecution_Report', '_test_report', '_test_execution_report']
            for suffix in suffixes:
                if suffix in feature_name:
                    feature_name = feature_name.replace(suffix, '')
            
            feature_normalized = feature_name.lower().replace(' ', '').replace('_', '')
            feature_display = feature_name.replace('_', ' ')
            
            print(f"\nProcessing: {feature_display}")
            
            # Determine sheet
            sheet_name = 'Sheet'
            if 'projectgroupings' in feature_normalized:
                sheet_name = 'Test Cases'
            elif 'readytowork' in feature_normalized:
                sheet_name = 'test_cases'
            
            # Load workbook
            try:
                wb = load_workbook(filepath, read_only=True, data_only=True)
                if sheet_name in wb.sheetnames:
                    ws = wb[sheet_name]
                else:
                    ws = wb.active
            except:
                print(f"  ❌ Error reading file")
                continue
            
            if not ws:
                print(f"  → Empty file, SKIPPED")
                continue
            
            # Get headers
            headers = {}
            for col_idx, cell in enumerate(next(ws.iter_rows(min_row=1, max_row=1))):
                if cell.value:
                    headers[cell.value] = col_idx
            
            # Find status column
            status_col = None
            status_names = ['status', 'execution status', 'execution_status', 'test result', 'result']
            for status_name in status_names:
                for header, idx in headers.items():
                    if str(header).lower().strip() == status_name:
                        status_col = idx
                        break
                if status_col:
                    break
            
            if status_col is None:
                print(f"  → No Status column found, SKIPPED")
                continue
            
            # Check for ID column
            id_col = None
            for header, idx in headers.items():
                if str(header).lower() in ['id', 'test id', 'tc id']:
                    id_col = idx
                    break
            
            # Count statuses
            pass_count = 0
            fail_count = 0
            not_executed = 0
            test_rows = 0
            
            for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
                # Skip empty rows
                if not any(row):
                    continue
                
                # If ID column exists, only count rows with ID
                if id_col is not None:
                    if row[id_col] is None:
                        continue
                
                test_rows += 1
                
                # Get status value
                if status_col < len(row) and row[status_col]:
                    status = str(row[status_col]).strip().lower()
                    if status == 'pass':
                        pass_count += 1
                    elif status == 'fail':
                        fail_count += 1
                    elif status in ['no run', 'not executed', 'not run', 'skipped', 'blocked']:
                        not_executed += 1
            
            if test_rows == 0:
                print(f"  → No test data found, SKIPPED")
                continue
            
            # Calculate pass rate
            total_executed = pass_count + fail_count + not_executed
            pass_rate = (pass_count / total_executed * 100) if total_executed > 0 else 0
            
            # Risk level
            if pass_rate < 50:
                risk = 'Critical'
            elif pass_rate < 75:
                risk = 'High'
            else:
                risk = 'Low'
            
            # Look for a defects/bugs sheet in the same workbook
            sheet_lookup = {name.lower(): name for name in wb.sheetnames}
            bug_ws = None
            for candidate in ('defects', 'bugs'):
                if candidate in sheet_lookup:
                    bug_ws = wb[sheet_lookup[candidate]]
                    break
            bugs = parse_bug_sheet(bug_ws) if bug_ws is not None else blank_bug_counts()

            # Add to features
            features[feature_display] = {
                'total': total_executed,
                'passed': pass_count,
                'failed': fail_count,
                'not_executed': not_executed,
                'pass_rate': round(pass_rate, 1),
                'risk': risk,
                'bugs': bugs
            }

            total_pass += pass_count
            total_fail += fail_count
            total_not_executed += not_executed
            total_tests += total_executed
            files_loaded += 1

            bug_summary['total'] += bugs['total']
            for sev, count in bugs['severity'].items():
                bug_summary['severity'][sev] += count
            for pri, count in bugs['priority'].items():
                bug_summary['priority'][pri] += count

            print(f"  ✅ {total_executed} tests: {pass_count} Pass, {fail_count} Fail, {not_executed} Not Executed ({pass_rate:.1f}%)")
            if bugs['total']:
                print(f"     🐞 {bugs['total']} bugs: {bugs['severity']}")
            wb.close()
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            continue
    
    # Overall stats
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
        'bug_summary': bug_summary,
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
    <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M50 10 A40 40 0 0 1 90 50 L75 50 A25 25 0 0 0 50 25 Z' fill='%2332cccd'/%3E%3Cpath d='M90 50 A40 40 0 0 1 50 90 L50 75 A25 25 0 0 0 75 50 Z' fill='%23ffe47a'/%3E%3Cpath d='M50 90 A40 40 0 0 1 10 50 L25 50 A25 25 0 0 0 50 75 Z' fill='%23ff6766'/%3E%3Cpath d='M10 50 A40 40 0 0 1 50 10 L50 25 A25 25 0 0 0 25 50 Z' fill='%23395e73'/%3E%3C/svg%3E">
    <style>
        :root {
            --teal: #32cccd;
            --yellow: #ffe47a;
            --coral: #ff6766;
            --navy: #395e73;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto; background: radial-gradient(circle at 15% 0%, #12222a 0%, #05070a 45%, #050608 100%); color: #e5e7eb; min-height: 100vh; padding: 0 0 40px; }
        .top-accent { height: 4px; width: 100%; background: linear-gradient(90deg, var(--teal), var(--yellow), var(--coral), var(--navy)); }
        .container { max-width: 1400px; margin: 0 auto; padding: 0 24px; }
        .brand-bar { display: flex; align-items: center; justify-content: space-between; padding: 18px 0; border-bottom: 1px solid rgba(75, 85, 99, 0.25); margin-bottom: 32px; flex-wrap: wrap; gap: 12px; }
        .brand-left { display: flex; align-items: center; gap: 10px; }
        .brand-left svg { display: block; }
        .brand-name { font-size: 15px; letter-spacing: 1px; font-weight: 700; color: #f3f4f6; }
        .brand-name span { font-weight: 400; color: #9ca3af; }
        .brand-tag { font-size: 11px; color: #6b7280; letter-spacing: 0.5px; text-transform: uppercase; }
        header { margin-bottom: 32px; }
        h1 { font-size: 32px; font-weight: 800; margin-bottom: 6px; color: #f9fafb; letter-spacing: -0.5px; }
        h1 .accent { background: linear-gradient(135deg, var(--teal) 0%, var(--yellow) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .subtitle { color: #9ca3af; font-size: 14px; }
        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .kpi-card { background: rgba(24, 28, 36, 0.85); border: 1px solid rgba(75, 85, 99, 0.3); border-top: 3px solid var(--teal); border-radius: 12px; padding: 20px; transition: transform 0.15s ease, border-color 0.15s ease; }
        .kpi-card:hover { transform: translateY(-2px); border-color: rgba(50, 204, 205, 0.5); }
        .kpi-card:nth-child(2) { border-top-color: var(--yellow); }
        .kpi-card:nth-child(3) { border-top-color: var(--coral); }
        .kpi-label { font-size: 12px; color: #9ca3af; text-transform: uppercase; margin-bottom: 10px; font-weight: 600; letter-spacing: 0.5px; }
        .kpi-value { font-size: 28px; font-weight: 700; margin-bottom: 5px; }
        .green { color: #34d399; }
        .blue { color: #60a5fa; }
        .section-title { font-size: 20px; font-weight: 700; margin-bottom: 20px; margin-top: 34px; color: #f3f4f6; display: flex; align-items: center; gap: 8px; }
        .section-title::before { content: ''; width: 4px; height: 20px; background: linear-gradient(180deg, var(--teal), var(--navy)); border-radius: 2px; display: inline-block; }
        table { width: 100%; border-collapse: collapse; background: rgba(24, 28, 36, 0.85); border: 1px solid rgba(75, 85, 99, 0.3); border-radius: 12px; overflow: hidden; }
        th { padding: 15px; text-align: left; font-weight: 600; font-size: 13px; background: rgba(55, 65, 81, 0.5); border-bottom: 1px solid rgba(75, 85, 99, 0.3); color: #d1d5db; }
        td { padding: 15px; border-bottom: 1px solid rgba(75, 85, 99, 0.1); }
        tr:hover { background: rgba(50, 204, 205, 0.05); }
        .risk-badge { display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        .risk-critical { background: rgba(239, 68, 68, 0.2); color: #fca5a5; }
        .risk-high { background: rgba(245, 158, 11, 0.2); color: #fcd34d; }
        .risk-low { background: rgba(16, 185, 129, 0.2); color: #86efac; }
        .pass-rate-cell { display: flex; flex-direction: column; align-items: center; gap: 6px; }
        .pass-rate-bar-track { width: 90px; height: 5px; border-radius: 3px; background: rgba(75, 85, 99, 0.3); overflow: hidden; }
        .pass-rate-bar-fill { height: 100%; border-radius: 3px; }
        .bug-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .bug-card { background: rgba(24, 28, 36, 0.85); border: 1px solid rgba(75, 85, 99, 0.3); border-radius: 12px; padding: 18px; border-left: 4px solid; transition: transform 0.15s ease; }
        .bug-card:hover { transform: translateY(-2px); }
        .bug-card-label { font-size: 12px; color: #9ca3af; text-transform: uppercase; margin-bottom: 8px; font-weight: 600; }
        .bug-card-value { font-size: 26px; font-weight: 700; }
        .bug-critical { border-left-color: #ef4444; }
        .bug-critical .bug-card-value { color: #fca5a5; }
        .bug-high { border-left-color: #f59e0b; }
        .bug-high .bug-card-value { color: #fcd34d; }
        .bug-medium { border-left-color: #60a5fa; }
        .bug-medium .bug-card-value { color: #93c5fd; }
        .bug-low { border-left-color: #10b981; }
        .bug-low .bug-card-value { color: #86efac; }
        .bug-count-badge { display: inline-block; min-width: 28px; padding: 3px 10px; border-radius: 4px; font-size: 13px; font-weight: 600; }
        .subsection-title { font-size: 15px; font-weight: 600; color: #9ca3af; margin: 20px 0 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        .footer { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; color: #6b7280; font-size: 12px; margin-top: 34px; padding-top: 20px; border-top: 1px solid rgba(75, 85, 99, 0.2); }
        .footer-brand { display: flex; align-items: center; gap: 6px; }
        .footer-brand svg { display: block; }
    </style>
</head>
<body>
    <div class="top-accent"></div>
    <div class="container">
        <div class="brand-bar">
            <div class="brand-left">
                <svg viewBox="0 0 100 100" width="26" height="26">
                    <path d="M50 10 A40 40 0 0 1 90 50 L75 50 A25 25 0 0 0 50 25 Z" fill="#32cccd"></path>
                    <path d="M90 50 A40 40 0 0 1 50 90 L50 75 A25 25 0 0 0 75 50 Z" fill="#ffe47a"></path>
                    <path d="M50 90 A40 40 0 0 1 10 50 L25 50 A25 25 0 0 0 50 75 Z" fill="#ff6766"></path>
                    <path d="M10 50 A40 40 0 0 1 50 10 L50 25 A25 25 0 0 0 25 50 Z" fill="#395e73"></path>
                </svg>
                <span class="brand-name">DAAS <span>LABS</span></span>
            </div>
            <span class="brand-tag">Data &amp; AI Execution Partner</span>
        </div>

        <header>
            <h1>📊 FieldTrax <span class="accent">QA Dashboard</span></h1>
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

        <h2 class="section-title">🐞 Bug Classification</h2>

        <div class="subsection-title">By Severity</div>
        <div class="bug-grid" id="bugSeverityGrid"></div>

        <div class="subsection-title">By Priority</div>
        <div class="bug-grid" id="bugPriorityGrid"></div>

        <div class="subsection-title">By Feature</div>
        <table>
            <thead>
                <tr>
                    <th>Feature</th>
                    <th style="text-align: center;">Total Bugs</th>
                    <th style="text-align: center;">Critical</th>
                    <th style="text-align: center;">High</th>
                    <th style="text-align: center;">Medium</th>
                    <th style="text-align: center;">Low</th>
                </tr>
            </thead>
            <tbody id="bugsByFeatureBody"></tbody>
        </table>

        <div class="footer">
            <div class="footer-brand">
                <svg viewBox="0 0 100 100" width="14" height="14">
                    <path d="M50 10 A40 40 0 0 1 90 50 L75 50 A25 25 0 0 0 50 25 Z" fill="#32cccd"></path>
                    <path d="M90 50 A40 40 0 0 1 50 90 L50 75 A25 25 0 0 0 75 50 Z" fill="#ffe47a"></path>
                    <path d="M50 90 A40 40 0 0 1 10 50 L25 50 A25 25 0 0 0 50 75 Z" fill="#ff6766"></path>
                    <path d="M10 50 A40 40 0 0 1 50 10 L50 25 A25 25 0 0 0 25 50 Z" fill="#395e73"></path>
                </svg>
                <span>Powered by DaaS Labs</span>
            </div>
            <div id="timestamp"></div>
        </div>
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
        
        const barColor = rate => rate >= 75 ? '#34d399' : rate >= 50 ? '#fbbf24' : '#f87171';

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
                    <td style="text-align: center;">
                        <div class="pass-rate-cell">
                            <strong>${stats.pass_rate}%</strong>
                            <div class="pass-rate-bar-track"><div class="pass-rate-bar-fill" style="width:${stats.pass_rate}%; background:${barColor(stats.pass_rate)};"></div></div>
                        </div>
                    </td>
                    <td style="text-align: center;">
                        <span class="risk-badge ${riskClass}">${stats.risk}</span>
                    </td>
                </tr>
            `;
        });
        
        // Add TOTAL row
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

        // ---- Bug Classification ----
        const bugSummary = data.bug_summary || { total: 0, severity: {}, priority: {} };
        const sevOrder = ['Critical', 'High', 'Medium', 'Low'];
        const sevClass = { Critical: 'bug-critical', High: 'bug-high', Medium: 'bug-medium', Low: 'bug-low' };

        let sevHtml = '';
        sevOrder.forEach(sev => {
            const count = (bugSummary.severity && bugSummary.severity[sev]) || 0;
            sevHtml += `
                <div class="bug-card ${sevClass[sev]}">
                    <div class="bug-card-label">${sev}</div>
                    <div class="bug-card-value">${count}</div>
                </div>
            `;
        });
        sevHtml += `
            <div class="bug-card" style="border-left-color:#9ca3af;">
                <div class="bug-card-label">Total Bugs</div>
                <div class="bug-card-value" style="color:#e5e7eb;">${bugSummary.total || 0}</div>
            </div>
        `;
        document.getElementById('bugSeverityGrid').innerHTML = sevHtml;

        const priOrder = ['P1', 'P2', 'P3'];
        let priHtml = '';
        priOrder.forEach(pri => {
            const count = (bugSummary.priority && bugSummary.priority[pri]) || 0;
            priHtml += `
                <div class="bug-card bug-high" style="border-left-color:#818cf8;">
                    <div class="bug-card-label">${pri}</div>
                    <div class="bug-card-value" style="color:#a5b4fc;">${count}</div>
                </div>
            `;
        });
        document.getElementById('bugPriorityGrid').innerHTML = priHtml;

        let bugsFeatureHtml = '';
        Object.entries(data.features).forEach(([name, stats]) => {
            const b = stats.bugs || { total: 0, severity: {} };
            const s = b.severity || {};
            bugsFeatureHtml += `
                <tr>
                    <td><strong>${name}</strong></td>
                    <td style="text-align: center;"><strong>${b.total || 0}</strong></td>
                    <td style="text-align: center;">${(s.Critical || 0) ? `<span class="bug-count-badge bug-critical" style="background:rgba(239,68,68,0.2); color:#fca5a5;">${s.Critical}</span>` : '0'}</td>
                    <td style="text-align: center;">${(s.High || 0) ? `<span class="bug-count-badge bug-high" style="background:rgba(245,158,11,0.2); color:#fcd34d;">${s.High}</span>` : '0'}</td>
                    <td style="text-align: center;">${(s.Medium || 0) ? `<span class="bug-count-badge bug-medium" style="background:rgba(96,165,250,0.2); color:#93c5fd;">${s.Medium}</span>` : '0'}</td>
                    <td style="text-align: center;">${(s.Low || 0) ? `<span class="bug-count-badge bug-low" style="background:rgba(16,185,129,0.2); color:#86efac;">${s.Low}</span>` : '0'}</td>
                </tr>
            `;
        });
        bugsFeatureHtml += `
            <tr style="background: rgba(75, 85, 99, 0.3); border-top: 2px solid rgba(75, 85, 99, 0.5); font-weight: bold;">
                <td><strong>TOTAL</strong></td>
                <td style="text-align: center;"><strong>${bugSummary.total || 0}</strong></td>
                <td style="text-align: center;"><strong>${(bugSummary.severity && bugSummary.severity.Critical) || 0}</strong></td>
                <td style="text-align: center;"><strong>${(bugSummary.severity && bugSummary.severity.High) || 0}</strong></td>
                <td style="text-align: center;"><strong>${(bugSummary.severity && bugSummary.severity.Medium) || 0}</strong></td>
                <td style="text-align: center;"><strong>${(bugSummary.severity && bugSummary.severity.Low) || 0}</strong></td>
            </tr>
        `;
        document.getElementById('bugsByFeatureBody').innerHTML = bugsFeatureHtml;

        document.getElementById('timestamp').textContent =
            `Updated: ${summary.last_updated} | Files: ${summary.files_loaded}/10 | Tests: ${summary.total_tests} | Bugs: ${bugSummary.total || 0}`;
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 FieldTrax QA Dashboard - No Pandas Version")
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
