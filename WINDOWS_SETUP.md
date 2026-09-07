# 🪟 QA Dashboard Setup - Windows Only

**You're on Windows? Perfect! Follow these steps instead.**

Time needed: 10 minutes

---

## ✅ Step 1: Check You Have Python

Open **Command Prompt** (press Windows key, type `cmd`, press Enter)

Copy and paste:
```
python --version
```

**Good result:** Shows `Python 3.11` or higher  
**Bad result:** Shows "not recognized" - Go to https://www.python.org/downloads/, download Python, install it, **CHECK "Add to PATH"**

---

## 📁 Step 2: Open Your Folder

In Command Prompt, type:
```
cd qa_analytics_platform
```

(Replace `qa_analytics_platform` with your actual folder name)

Verify you're in the right place - type:
```
dir
```

You should see: `app.py`, `requirements.txt`, `setup.sh`, etc.

---

## 🔧 Step 3: Create Virtual Environment

This creates a safe space for Python packages.

Copy and paste:
```
python -m venv venv
```

Wait for it to finish (you'll see a new `venv` folder created).

---

## ▶️ Step 4: Activate Virtual Environment

Copy and paste:
```
venv\Scripts\activate
```

**Success:** You should see `(venv)` at the start of your line.

Example:
```
(venv) C:\Users\mkumar9\qa_analytics_platform>
```

---

## 📦 Step 5: Install Python Packages

Copy and paste:
```
pip install -r requirements.txt
```

This downloads and installs all the software your dashboard needs.

**Wait for it to finish.** You'll see lots of text - that's normal.

When done, you should see:
```
Successfully installed flask pandas scikit-learn ...
```

---

## 🗄️ Step 6: Create the Database

Copy and paste:
```
python
```

Now you're in Python. Copy and paste this:
```python
from app import app, db
with app.app_context():
    db.create_all()
    print("Database created!")
```

Press Enter. You should see `Database created!`

Then type:
```
exit()
```

---

## ▶️ Step 7: Start the Dashboard

Copy and paste:
```
python app.py
```

**You should see:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

**Done!** Your dashboard is running! ✅

---

## 📤 Step 8: Upload Your Test Files

**Open a NEW Command Prompt window** (keep the first one running)

Type:
```
cd qa_analytics_platform
```

Now upload your test file. Copy and paste (change the filename):
```
curl -X POST -F "file=@DraftJob_Test_execution_report.xlsx" http://localhost:5000/api/upload
```

**You should see:**
```json
{"status": "success", "message": "Successfully imported 57 records"}
```

**Upload more files** the same way:
```
curl -X POST -F "file=@BranchOverhead_TestExecution_Report.xlsx" http://localhost:5000/api/upload
```

---

## 📊 Step 9: View Your Analytics

In the same Command Prompt window, copy and paste:

**See overall summary:**
```
curl http://localhost:5000/api/summary
```

**See 7-day forecast:**
```
curl http://localhost:5000/api/forecast/DraftJob
```

**See anomalies:**
```
curl http://localhost:5000/api/anomalies
```

**See risk assessment:**
```
curl http://localhost:5000/api/risk/DraftJob
```

---

## 🎯 Summary

| What | Command |
|------|---------|
| Create environment | `python -m venv venv` |
| Activate environment | `venv\Scripts\activate` |
| Install packages | `pip install -r requirements.txt` |
| Create database | `python` then `from app import app, db` and `with app.app_context(): db.create_all()` |
| Start dashboard | `python app.py` |
| Upload file | `curl -X POST -F "file=@filename.xlsx" http://localhost:5000/api/upload` |
| View summary | `curl http://localhost:5000/api/summary` |
| View forecast | `curl http://localhost:5000/api/forecast/FeatureName` |
| Stop dashboard | `CTRL + C` |

---

## ❓ Troubleshooting

### **Error: "Python not found"**
- You didn't install Python or didn't check "Add to PATH"
- Download Python again: https://www.python.org/downloads/
- **IMPORTANT:** Check "Add Python to PATH" during install
- Restart Command Prompt after installing

### **Error: "No such file"**
- Make sure you're in the right folder
- Type `dir` and you should see `app.py`

### **Error: "Port already in use"**
- Close other applications
- Or edit `.env` and change `API_PORT=5000` to `API_PORT=5001`

### **Error: "curl not found"**
- Windows Command Prompt doesn't have curl by default
- Install Git for Windows: https://git-scm.com/download/win
- Then use Git Bash instead of Command Prompt
- Or use PowerShell: Press Windows key, type `powershell`, press Enter

### **Dashboard won't start**
- Make sure you activated the environment: `venv\Scripts\activate`
- Make sure you see `(venv)` at the start of your line
- Make sure you installed packages: `pip install -r requirements.txt`

### **Still stuck?**
- Make sure all files are in the same folder: `dir` should show `app.py`
- Make sure you have Python 3.11+: `python --version`
- Make sure you're using Command Prompt or PowerShell, not bash

---

## ✅ Quick Test

When dashboard is running, open a new Command Prompt and type:
```
curl http://localhost:5000/api/health
```

You should see:
```json
{"status":"healthy","version":"2.0.0",...}
```

If you see this, **everything is working!** 🎉

---

## 📞 Commands Summary

**First time setup:**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

**After first time (just restart):**
```
venv\Scripts\activate
python app.py
```

**To stop dashboard:**
```
CTRL + C
```

**To deactivate environment when done:**
```
deactivate
```

---

## 🎉 You're Set!

You now have a working QA dashboard on Windows!

**Next:** Follow Step 8 to upload your test files and start using it.

Questions? Ask me!
