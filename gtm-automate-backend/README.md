# GTM Automation - Python Project

Automate Google Tag Manager workspace creation and populate it with **variables, triggers, and tags** from JSON or Excel files using Google Service Account authentication.

---

## 🚀 Features

✅ **Automated Workspace Creation** - Creates new GTM workspace with timestamp  
✅ **Bulk Resource Creation** - Variables, Triggers, Tags from single file  
✅ **Multiple Input Formats** - Support for JSON and Excel (.xlsx)  
✅ **Schema Validation** - Validates input before GTM API calls  
✅ **Error Handling** - Continues processing even if individual items fail  
✅ **Trigger Mapping** - Automatically links tags to triggers  
✅ **CLI Interface** - Easy command-line execution  
✅ **Dry Run Mode** - Validate input without creating resources  

---

## 📂 Project Structure

```
gtm-automation/
├── app.py                              # Main entry point
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variable template
├── .gitignore                          # Git ignore rules
├── FLOW_STRUCTURE.md                   # Detailed flow documentation
│
├── src/                                # Source code
│   ├── __init__.py
│   ├── config.py                       # Configuration management
│   ├── gtm_client.py                   # GTM API client
│   ├── parser.py                       # JSON/Excel parser
│   ├── schema.py                       # Data validation
│   └── utils/
│       ├── __init__.py
│       └── helpers.py                  # Helper functions
│
├── config/                             # Configuration files
│   └── service_account.json.example    # Service account template
│
├── data/                               # Sample input files
│   └── sample_input.json               # Sample JSON input
│
├── templates/                          # Tag templates
│   └── fb_pageview.html                # Facebook Pixel template
│
├── tests/                              # Unit tests
│   ├── __init__.py
│   ├── test_app.py
│   ├── test_gtm_client.py
│   └── test_parser.py
│
└── logs/                               # Log files (auto-generated)
    └── gtm_automation.log
```

---

## 🔧 Installation

### 1. Clone or Download the Project

```bash
cd "d:\GTM Automate"
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## ⚙️ Configuration

### 1. Create Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Tag Manager API**
4. Create **Service Account** with Editor permissions
5. Download JSON key file
6. Save as `config/service_account.json`

### 2. Setup Environment Variables

```powershell
cp .env.example .env
```

Edit `.env` file:

```env
GTM_ACCOUNT_ID=123456789
GTM_CONTAINER_ID=12345678
SERVICE_ACCOUNT_JSON_PATH=config/service_account.json
WORKSPACE_NAME_PREFIX=AutoGen
LOG_LEVEL=INFO
```

### 3. Grant Service Account Access

1. Open [Google Tag Manager](https://tagmanager.google.com/)
2. Go to **Admin** → **User Management**
3. Add service account email with **Edit** permissions

---

## 📝 Input File Format

### JSON Format

```json
{
  "variables": [
    {
      "name": "Page URL",
      "type": "u",
      "parameter": [
        {"key": "component", "type": "template", "value": "URL"}
      ]
    }
  ],
  "triggers": [
    {
      "name": "All Pages",
      "type": "PAGEVIEW"
    },
    {
      "name": "Purchase Event",
      "type": "CUSTOM_EVENT",
      "customEventFilter": [...]
    }
  ],
  "tags": [
    {
      "name": "GA4 Pageview",
      "type": "gaawe",
      "parameter": [
        {"key": "measurementId", "type": "template", "value": "G-XXXXXXX"}
      ],
      "firingTriggerId": ["All Pages"]
    }
  ]
}
```

### Excel Format

Create Excel file with 3 sheets:

**Sheet: Variables**
| name | type | value | parameter_key | parameter_value |
|------|------|-------|---------------|-----------------|
| Page URL | u | | component | URL |

**Sheet: Triggers**
| name | type | event_name |
|------|------|------------|
| All Pages | PAGEVIEW | |
| Purchase | CUSTOM_EVENT | purchase |

**Sheet: Tags**
| name | type | html | firing_triggers |
|------|------|------|-----------------|
| FB Pixel | html | &lt;script&gt;...&lt;/script&gt; | All Pages |

---

## 🎯 Usage

### Basic Usage

```powershell
python app.py --input data/sample_input.json
```

### Custom Workspace Name

```powershell
python app.py --input data/sample_input.json --workspace "Black Friday 2025"
```

### Verbose Logging

```powershell
python app.py --input data/sample_input.json --verbose
```

### Dry Run (Validation Only)

```powershell
python app.py --input data/sample_input.json --dry-run
```

---

## 📊 Output Example

```
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

🔗 Open GTM Workspace: https://tagmanager.google.com/#/...

➡️  Next Step: Review the workspace and click 'Submit' in GTM UI
```

---

## 🧪 Testing

Run unit tests:

```powershell
python -m unittest discover tests
```

Run specific test:

```powershell
python -m unittest tests.test_gtm_client
```

---

## 🔍 Troubleshooting

### Authentication Error

**Error:** `Authentication failed`

**Solution:**
- Verify `service_account.json` exists and is valid
- Check service account has GTM API access
- Ensure service account added to GTM container with Edit permissions

### Configuration Error

**Error:** `GTM_ACCOUNT_ID is not set`

**Solution:**
- Copy `.env.example` to `.env`
- Fill in all required values
- Restart application

### Validation Error

**Error:** `Input data validation failed`

**Solution:**
- Check JSON/Excel structure matches expected format
- Ensure all required fields are present
- Validate trigger names referenced in tags exist

---

## 📚 API Documentation

- [GTM API v2 Reference](https://developers.google.com/tag-platform/tag-manager/api/v2)
- [Service Account Setup](https://cloud.google.com/iam/docs/service-accounts)
- [GTM Tag Types](https://developers.google.com/tag-platform/tag-manager/api/v2/reference/tag-types)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

MIT License - feel free to use this project for commercial or personal use.

---

## 🙋 Support

For issues or questions:
- Check [FLOW_STRUCTURE.md](FLOW_STRUCTURE.md) for detailed flow
- Review sample files in `data/` folder
- Open GitHub issue with error logs

---

## 🎉 Quick Start Checklist

- [ ] Install Python 3.8+
- [ ] Create virtual environment
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Setup Google Cloud Service Account
- [ ] Download service account JSON
- [ ] Configure `.env` file
- [ ] Grant GTM access to service account
- [ ] Prepare input JSON/Excel file
- [ ] Run: `python app.py --input your_file.json`
- [ ] Open GTM and review workspace
- [ ] Click "Submit" in GTM UI

---

**Made with ❤️ for GTM Automation**
