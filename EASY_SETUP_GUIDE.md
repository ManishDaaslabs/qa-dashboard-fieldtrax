# 🚀 QA Dashboard Setup - Super Easy Guide

**Time needed:** 10 minutes  
**Difficulty:** Beginner-friendly  
**What you'll have at the end:** A working QA dashboard with AI predictions

---

## 📋 What You'll Do

1. ✅ Download and set up the application (3 min)
2. ✅ Start the dashboard (2 min)
3. ✅ Upload your test reports (2 min)
4. ✅ View your analytics (3 min)

**That's it!**

---

## 🎯 Step 1: Download Everything (1 minute)

You should already have these 13 files:
- `app.py`
- `frontend.jsx`
- `requirements.txt`
- `setup.sh`
- `docker-compose.yml`
- `Dockerfile`
- `nginx.conf`
- `.env`
- `.env.example`
- `README.md`
- `GETTING_STARTED.md`
- `API_EXAMPLES.md`
- `BUILD_SUMMARY.md`

**Create a folder** on your computer called `qa_analytics_platform` and **put all these files in it**.

---

## 🔧 Step 2: Install Python (If You Don't Have It)

**Check if you have Python:**

Open your **Terminal** (Mac/Linux) or **Command Prompt** (Windows) and type:
```
python --version
```

If you see a version number (like `Python 3.11`), you're good! Skip to Step 3.

**If not, download Python:**
1. Go to https://www.python.org/downloads/
2. Download the latest Python 3.11+ version
3. Run the installer
4. **IMPORTANT:** Check the box that says "Add Python to PATH"
5. Click Install

---

## ⚡ Step 3: Set Up the Application (3 minutes)

**Open Terminal/Command Prompt** and navigate to your folder:

```
cd qa_analytics_platform
```

**Now run the setup (copy and paste this):**

### **On Mac or Linux:**
```bash
bash setup.sh dev
```

### **On Windows:**
```bash
bash setup.sh dev
```

**What this does:**
- Creates a virtual environment (a safe space for Python packages)
- Installs all required software
- Sets up the database
- Creates the `.env` configuration file

**You'll see lots of text scrolling—that's normal!** Wait for it to finish.

**When done, you'll see:**
```
✓ Development environment setup complete!
```

---

## ▶️ Step 4: Start the Dashboard (2 minutes)

**Still in the Terminal, type these commands one by one:**

### **Activate the environment:**

**On Mac or Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your Terminal line. That means it's activated.

**Start the application:**
```bash
python app.py
```

**You should see:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

**Congratulations!** Your dashboard is now running! 🎉

---

## 📊 Step 5: Access Your Dashboard (1 minute)

**Open your web browser** and go to:
```
http://localhost:5000/api/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2026-09-04T...",
  "version": "2.0.0"
}
```

This means it's working!

---

## 📤 Step 6: Upload Your Test Reports (2 minutes)

You have test execution files like:
- `DraftJob_Test_execution_report.xlsx`
- `BranchOverhead_TestExecution_Report.xlsx`
- etc.

**Open a NEW Terminal window** (keep the first one running) and type:

```bash
cd qa_analytics_platform
```

**Upload your first test report:**
```bash
curl -X POST -F "file=@DraftJob_Test_execution_report.xlsx" http://localhost:5000/api/upload
```

**Expected result:**
```json
{
  "status": "success",
  "message": "Successfully imported 57 records",
  "records_inserted": 57
}
```

**Upload more reports** the same way:
```bash
curl -X POST -F "file=@BranchOverhead_TestExecution_Report.xlsx" http://localhost:5000/api/upload
```

Keep doing this for each Excel file you have.

---

## 📈 Step 7: View Your Analytics (2 minutes)

**In the same Terminal window, type these commands to see your data:**

**See overall summary:**
```bash
curl http://localhost:5000/api/summary
```

You'll see your pass rates, failed tests, defects, etc.

**See AI prediction for a feature:**
```bash
curl http://localhost:5000/api/forecast/DraftJob
```

You'll see predicted pass rates for the next 7 days!

**See detected problems:**
```bash
curl http://localhost:5000/api/anomalies
```

This shows unusual test failures automatically detected by AI.

**See which features are risky:**
```bash
curl http://localhost:5000/api/risk/DraftJob
```

This shows risk level and recommendations.

---

## 🎯 Summary of What You Have

| What | Where |
|------|-------|
| **Overall Stats** | `curl http://localhost:5000/api/summary` |
| **7-Day Forecast** | `curl http://localhost:5000/api/forecast/FeatureName` |
| **Anomalies** | `curl http://localhost:5000/api/anomalies` |
| **Risk Assessment** | `curl http://localhost:5000/api/risk/FeatureName` |

---

## 🛑 How to Stop the Dashboard

**In the Terminal running the dashboard**, press:
```
CTRL + C
```

This stops the application. You can restart it anytime by running:
```bash
source venv/bin/activate
python app.py
```

---

## ❓ Troubleshooting (Common Problems)

### **Problem: "Python not found"**
- **Solution:** You need to install Python. Go to https://www.python.org/downloads/ and install it.

### **Problem: "Port 5000 already in use"**
- **Solution:** Something else is using that port. Either:
  - Close other applications
  - Or edit `.env` and change `API_PORT=5000` to `API_PORT=5001`

### **Problem: "No such file or directory: app.py"**
- **Solution:** Make sure you're in the right folder. Type: `ls` (Mac/Linux) or `dir` (Windows) and you should see `app.py` in the list.

### **Problem: Upload fails with "Unsupported file format"**
- **Solution:** Only `.xlsx` (Excel) and `.csv` files work. Make sure your file is one of these.

### **Problem: "ModuleNotFoundError: No module named 'flask'"**
- **Solution:** You skipped Step 2. Run: `bash setup.sh dev`

### **Problem: "command not found: bash"** (Windows)
- **Solution:** You might need to use Windows PowerShell or download Git Bash. Or type the commands manually:
  1. Create a folder `venv`
  2. Run: `python -m venv venv`
  3. Run: `venv\Scripts\activate`
  4. Run: `pip install -r requirements.txt`

---

## 🚀 Next: Make It Permanent

After you get it working locally, you might want to:

1. **Keep it running 24/7** - Use Docker (easier for production)
   - See `docker-compose.yml` file
   - Or ask me for help

2. **Share with your team** - Deploy to the cloud
   - AWS, Google Cloud, or Heroku
   - Or ask me for deployment help

3. **Add more data** - Upload new test reports anytime
   - Just run the `curl` upload command again

4. **Use the Web Dashboard** - Instead of Terminal commands
   - Copy `frontend.jsx` to a React app
   - Or ask me for a standalone HTML version

---

## ✅ Verify It's Working

**Run this command and you should get a response:**

```bash
curl http://localhost:5000/api/summary
```

**If you see JSON data back, you're good!** 

If you see "error" or "connection refused", the dashboard isn't running. Start it again with:
```bash
python app.py
```

---

## 📞 Quick Command Reference

| Task | Command |
|------|---------|
| Start dashboard | `python app.py` |
| Activate environment | `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\activate` (Windows) |
| Stop dashboard | `CTRL + C` |
| Upload test file | `curl -X POST -F "file=@filename.xlsx" http://localhost:5000/api/upload` |
| See summary | `curl http://localhost:5000/api/summary` |
| See forecast | `curl http://localhost:5000/api/forecast/FeatureName` |
| See anomalies | `curl http://localhost:5000/api/anomalies` |
| See risks | `curl http://localhost:5000/api/risk/FeatureName` |

---

## 🎉 You're Done!

You now have:
- ✅ A working QA dashboard
- ✅ AI predictions for test pass rates
- ✅ Automatic anomaly detection
- ✅ Risk assessment for each feature
- ✅ Root cause analysis

**All running on your computer, ready for your QA work!**

---

## 💡 Pro Tips

1. **Keep Terminal open** - The dashboard needs the Terminal window to stay running
2. **Upload reports regularly** - The more data, the better the predictions
3. **Check anomalies daily** - This alerts you to problems automatically
4. **Share results** - Copy the data from `curl` commands and paste into emails/reports
5. **Ask for help** - If something doesn't work, I'm here to help

---

## What Each AI Feature Does

### **Forecast** 
- Predicts if your tests will pass more or less next week
- Helps you plan resources
- Example: "DraftJob pass rate will be 95% next week"

### **Anomalies**
- Spots when tests suddenly start failing
- Alerts you automatically
- Example: "ProjectGroupings had unusual failures on Sept 3"

### **Risk Assessment**
- Tells you which features need attention
- Gives recommendations
- Example: "Break_Types is CRITICAL - needs immediate review"

### **Root Cause**
- Explains WHY tests are failing
- Shows trends and patterns
- Example: "Failures increasing 2% per week - investigate recent changes"

---

## 🎓 Learn More

For more details, see:
- **README.md** - Full technical documentation
- **API_EXAMPLES.md** - All commands and examples
- **GETTING_STARTED.md** - More detailed guide

But you don't need to read those to get started. This guide is enough!

---

**Ready to start? Go to Step 1 above and follow along!** 🚀

Questions? I'm here to help!
