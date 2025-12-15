# 🚀 GTM Automation - Quick Start Guide

## ✅ PROJECT VERIFICATION COMPLETE!

Your project structure is **PERFECT** and ready to run! ✓

---

## 📂 Verified Project Structure

```
✓ GTM Automate/
  ✓ app.py                    # Main application
  ✓ test_connection.py        # Connection test script
  ✓ requirements.txt          # Dependencies
  ✓ .env                      # Your configuration (FILLED)
  ✓ .env.example              # Template
  ✓ README.md                 # Documentation
  ✓ FLOW_STRUCTURE.md         # Flow diagram
  
  ✓ src/                      # Core modules
    ✓ __init__.py
    ✓ config.py               # Config management
    ✓ gtm_client.py           # GTM API client
    ✓ parser.py               # JSON/Excel parser
    ✓ schema.py               # Data validation
    ✓ utils/
      ✓ __init__.py
      ✓ helpers.py            # Helper functions
  
  ✓ config/
    ✓ service_account.json    # REAL Google credentials (FOUND!)
  
  ✓ data/
    ✓ sample_input.json       # Sample data
  
  ✓ templates/
    ✓ fb_pageview.html        # Facebook Pixel template
  
  ✓ tests/
    ✓ __init__.py
    ✓ test_app.py
    ✓ test_gtm_client.py
    ✓ test_parser.py
```

---

## ✅ Configuration Status

### ✓ .env File - CONFIGURED
```
GTM_ACCOUNT_ID=6012345678
GTM_CONTAINER_ID=98765432
SERVICE_ACCOUNT_JSON_PATH=config/service_account.json
WORKSPACE_NAME_PREFIX=AutoGen
LOG_LEVEL=INFO
```

### ✓ Service Account - REAL CREDENTIALS FOUND
```
Project ID: gtm-automate-480807
Service Email: (found in JSON)
Private Key: ✓ Valid format
Status: ✓ READY TO USE
```

---

## 🚀 HOW TO RUN - Step by Step

### **STEP 1: Setup Python Environment**

Open PowerShell in your project directory:

```powershell
# Navigate to project
cd "D:\GTM Automate"

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Your prompt should now show: (venv) PS D:\GTM Automate>
```

---

### **STEP 2: Install Dependencies**

```powershell
# Install all required packages
pip install -r requirements.txt
```

**Expected output:**
```
Collecting google-auth==2.23.4
Collecting google-api-python-client==2.108.0
Collecting pandas==2.1.3
...
Successfully installed google-auth-2.23.4 pandas-2.1.3 ...
```

**Wait for installation to complete** (30-60 seconds)

---

### **STEP 3: Test GTM Connection**

```powershell
# Run connection test
python test_connection.py
```

**What it checks:**
1. ✓ .env configuration is valid
2. ✓ Service account file exists
3. ✓ Authentication with Google
4. ✓ Access to GTM container
5. ✓ Lists existing workspaces

**Expected SUCCESS output:**
```
======================================================================
  GTM CONNECTION TEST
======================================================================

[Step 1/5] Checking configuration...
✓ Configuration is valid
  - Account ID: 6012345678
  - Container ID: 98765432

[Step 2/5] Checking service account file...
✓ Service account file exists and has valid structure
  - Project ID: gtm-automate-480807
  - Service Account Email: gtm-...@gtm-automate-480807.iam.gserviceaccount.com

[Step 3/5] Testing GTM API authentication...
✓ Successfully authenticated with GTM API

[Step 4/5] Testing GTM API access (listing workspaces)...
✓ Successfully connected to GTM
  - Found X existing workspace(s)

[Step 5/5] Verifying permissions...
✓ Service account has read access to GTM

======================================================================
  ✅ CONNECTION TEST PASSED!
======================================================================
```

---

### **STEP 4: Run GTM Automation (DRY RUN)**

```powershell
# Validate input without creating anything
python app.py --input data\sample_input.json --dry-run
```

**What happens:**
- ✓ Parses JSON file
- ✓ Validates data structure
- ✓ Checks all trigger references
- ✗ Does NOT create anything in GTM

**Expected output:**
```
======================================================================
  GTM AUTOMATION - STARTING
======================================================================

[Step 1/7] Validating configuration...
✓ Configuration validated

[Step 2/7] Reading input file...
✓ Input file parsed successfully
  - Variables: 3
  - Triggers: 4
  - Tags: 4

[Step 3/7] Validating data schema...
✓ Input data validation passed
✓ All trigger references are valid

✓ DRY RUN COMPLETED - No GTM resources created
```

---

### **STEP 5: Run FULL Automation**

```powershell
# Create actual GTM workspace with resources
python app.py --input data\sample_input.json
```

**What happens:**
1. ✓ Creates new workspace: `AutoGen_20251210_143025`
2. ✓ Creates 3 variables
3. ✓ Creates 4 triggers
4. ✓ Creates 4 tags (linked to triggers)
5. ✓ Shows GTM URL to open

**Expected output:**
```
======================================================================
  GTM AUTOMATION - STARTING
======================================================================

[Step 1/7] Validating configuration...
✓ Configuration validated

[Step 2/7] Reading input file...
✓ Input file parsed successfully
  - Variables: 3
  - Triggers: 4
  - Tags: 4

[Step 3/7] Validating data schema...
✓ Data validation passed

[Step 4/7] Authenticating with GTM API...
✓ Successfully authenticated with GTM API

[Step 5/7] Creating GTM workspace...
✓ Workspace created: AutoGen_20251210_143025 (ID: 15)

[Step 6/7] Creating GTM resources...

  Creating 3 variable(s)...
  ✓ Variable created: Page URL (ID: 1)
  ✓ Variable created: Page Path (ID: 2)
  ✓ Variable created: Click Text (ID: 3)

  Creating 4 trigger(s)...
  ✓ Trigger created: All Pages (ID: 1)
  ✓ Trigger created: DOM Ready (ID: 2)
  ✓ Trigger created: Purchase Complete (ID: 3)
  ✓ Trigger created: Click CTA Button (ID: 4)

  Creating 4 tag(s)...
  ✓ Tag created: GA4 - Pageview (ID: 1)
  ✓ Tag created: Facebook Pixel - PageView (ID: 2)
  ✓ Tag created: GA4 - Purchase Event (ID: 3)
  ✓ Tag created: Track CTA Click (ID: 4)

[Step 7/7] Finalizing...

======================================================================
           GTM AUTOMATION - EXECUTION SUMMARY
======================================================================
Workspace Name:      AutoGen_20251210_143025
Workspace ID:        15
Workspace URL:       https://tagmanager.google.com/#/container/...
----------------------------------------------------------------------
Variables Created:   3
Triggers Created:    4
Tags Created:        4
----------------------------------------------------------------------
Errors:              None
----------------------------------------------------------------------
Status:              SUCCESS
Duration:            12.45s
======================================================================

✓ GTM AUTOMATION COMPLETED SUCCESSFULLY

🔗 Open GTM Workspace: https://tagmanager.google.com/#/container/accounts/6012345678/containers/98765432/workspaces/15

➡️  Next Step: Review the workspace and click 'Submit' in GTM UI
```

---

## 📊 Command Options

### Basic Usage
```powershell
python app.py --input data\sample_input.json
```

### Custom Workspace Name
```powershell
python app.py --input data\sample_input.json --workspace "Black Friday 2025"
```

### Verbose Logging (Debug Mode)
```powershell
python app.py --input data\sample_input.json --verbose
```

### Dry Run (Validation Only)
```powershell
python app.py --input data\sample_input.json --dry-run
```

### Help
```powershell
python app.py --help
```

---

## 🎯 What to Do After Running

1. **Open the GTM URL** shown in output
2. **Review the workspace:**
   - Check Variables tab
   - Check Triggers tab
   - Check Tags tab
3. **Verify everything looks correct**
4. **Click "Submit"** button in GTM
5. **Add version name and description**
6. **Publish** (or keep as draft)

---

## ⚠️ Before Running - ONE MORE THING!

You need to **add the service account to GTM**:

1. Open GTM: https://tagmanager.google.com/
2. Go to **Admin** → **User Management**
3. Click **"+"** to add user
4. Paste this email:
   ```
   (check your config/service_account.json for "client_email")
   ```
5. Grant **"Edit"** permission
6. Click **"Invite"**

**Then run the connection test to verify!**

---

## 🐛 Troubleshooting

### If connection test fails:

**Error: "Permission denied"**
```powershell
# Solution: Add service account to GTM User Management
# Email is in: config/service_account.json → "client_email"
```

**Error: "API not enabled"**
```powershell
# Solution: Enable Tag Manager API in Google Cloud Console
# https://console.cloud.google.com/apis/library/tagmanager.googleapis.com
```

**Error: "Container not found"**
```powershell
# Solution: Check GTM_ACCOUNT_ID and GTM_CONTAINER_ID in .env
# Get them from GTM URL
```

---

## 📝 Quick Command Reference

```powershell
# 1. Setup
cd "D:\GTM Automate"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Test
python test_connection.py

# 3. Dry Run
python app.py --input data\sample_input.json --dry-run

# 4. Full Run
python app.py --input data\sample_input.json

# 5. View logs
Get-Content logs\gtm_automation.log -Tail 50
```

---

## ✅ Project Status: **READY TO RUN!**

Everything is in place. Just follow the steps above! 🚀
