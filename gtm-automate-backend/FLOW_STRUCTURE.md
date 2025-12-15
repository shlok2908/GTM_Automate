# GTM Automation - Complete Flow Structure

## 📋 Project Overview
Automates Google Tag Manager workspace creation and populates it with variables, triggers, and tags from JSON/Excel files using Service Account authentication.

---

## 🏗️ Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     GTM AUTOMATION FLOW                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│  Business Team       │
│  Prepares Input      │
│  (JSON/Excel)        │
└──────────┬───────────┘
           │
           │ Upload file
           ▼
┌────────────────────────────────────────────────────────────────┐
│                    APP.PY (Entry Point)                         │
│  • Parse CLI arguments                                          │
│  • Load configuration (.env)                                    │
│  • Initialize logging                                           │
│  • Validate config (Account ID, Container ID, Credentials)      │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                   PARSER.PY (File Parser)                       │
│  • Auto-detect file type (.json / .xlsx)                        │
│  • Read and parse input file                                    │
│  • Convert to standardized format                               │
│  • Extract: variables[], triggers[], tags[]                     │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                 SCHEMA.PY (Data Validation)                     │
│  • Validate JSON structure against schema                       │
│  • Check required fields exist                                  │
│  • Validate data types                                          │
│  • Verify trigger/tag type enums                                │
│  • Ensure trigger references are valid                          │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼ (If validation passes)
┌────────────────────────────────────────────────────────────────┐
│              GTM_CLIENT.PY (API Authentication)                 │
│  • Load service_account.json                                    │
│  • Authenticate with Google OAuth 2.0                           │
│  • Create GTM API service object                                │
│  • Set scope: tagmanager.edit.containers                        │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│              CREATE WORKSPACE (GTM_CLIENT.PY)                   │
│  • Generate workspace name: AutoGen_YYYYMMDD_HHMMSS             │
│  • API Call: POST /workspaces                                   │
│  • Store workspace_id and workspace_path                        │
│  • Log: "Workspace created: {name} (ID: {id})"                  │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│           PROCESS VARIABLES (Loop through input)                │
│                                                                  │
│  FOR EACH variable in data['variables']:                        │
│    ├─ Prepare variable body (name, type, parameters)            │
│    ├─ API Call: POST /workspaces/{id}/variables                 │
│    ├─ Store variable_id                                         │
│    └─ Log: "Variable created: {name}"                           │
│                                                                  │
│  Variables Created: N                                            │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│           PROCESS TRIGGERS (Loop through input)                 │
│                                                                  │
│  trigger_id_map = {}  # Store name -> ID mapping                │
│                                                                  │
│  FOR EACH trigger in data['triggers']:                          │
│    ├─ Prepare trigger body (name, type, filters)                │
│    ├─ API Call: POST /workspaces/{id}/triggers                  │
│    ├─ Store trigger_id                                          │
│    ├─ Map: trigger_id_map[trigger_name] = trigger_id            │
│    └─ Log: "Trigger created: {name} (ID: {id})"                 │
│                                                                  │
│  Triggers Created: N                                             │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│             PROCESS TAGS (Loop through input)                   │
│                                                                  │
│  FOR EACH tag in data['tags']:                                  │
│    ├─ Prepare tag body (name, type, parameters)                 │
│    ├─ Map firing_triggers names → IDs (using trigger_id_map)    │
│    ├─ Map blocking_triggers names → IDs (using trigger_id_map)  │
│    ├─ API Call: POST /workspaces/{id}/tags                      │
│    ├─ Store tag_id                                              │
│    └─ Log: "Tag created: {name} (ID: {id})"                     │
│                                                                  │
│  Tags Created: N                                                 │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                  GENERATE SUMMARY REPORT                        │
│  • Total Variables Created: X                                   │
│  • Total Triggers Created: Y                                    │
│  • Total Tags Created: Z                                        │
│  • Workspace URL: https://tagmanager.google.com/...             │
│  • Status: SUCCESS / PARTIAL / FAILED                           │
│  • Log errors if any                                            │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                   NOTIFY BUSINESS TEAM                          │
│  • Send email/webhook notification (optional)                   │
│  • Provide GTM workspace link                                   │
│  • Team opens GTM → Reviews → Clicks "Submit"                   │
│  • No manual configuration needed!                              │
└────────────────────────────────────────────────────────────────┘
```

---

## 📂 File Structure & Responsibilities

```
gtm-automate/
│
├── app.py                          # 🎯 MAIN ENTRY POINT
│   ├─ Parse CLI arguments
│   ├─ Load configuration
│   ├─ Orchestrate entire workflow
│   ├─ Error handling & logging
│   └─ Generate final report
│
├── config.py                       # ⚙️ CONFIGURATION
│   ├─ Load environment variables
│   ├─ Validate GTM credentials
│   ├─ Define constants & settings
│   └─ Export Config class
│
├── gtm_client.py                   # 🔌 GTM API CLIENT
│   ├─ Authenticate with Service Account
│   ├─ create_workspace()
│   ├─ create_variable()
│   ├─ create_trigger()
│   ├─ create_tag()
│   ├─ list_workspaces()
│   └─ Handle API errors & retries
│
├── parser.py                       # 📄 FILE PARSER
│   ├─ parse_json() - Read JSON files
│   ├─ parse_excel() - Read Excel files
│   ├─ _parse_variables_sheet()
│   ├─ _parse_triggers_sheet()
│   ├─ _parse_tags_sheet()
│   └─ Normalize data structure
│
├── schema.py                       # ✅ VALIDATION
│   ├─ Define JSON schema
│   ├─ validate_input_data()
│   ├─ Check required fields
│   ├─ Validate data types
│   └─ Verify relationships
│
├── utils.py                        # 🛠️ UTILITIES
│   ├─ setup_logging()
│   ├─ retry_on_failure()
│   ├─ generate_workspace_name()
│   ├─ format_summary()
│   └─ send_notification()
│
├── requirements.txt                # 📦 DEPENDENCIES
├── .env.example                    # 🔐 CONFIG TEMPLATE
├── .gitignore                      # 🚫 IGNORE RULES
│
├── sample_input.json               # 📋 SAMPLE INPUT
├── sample_input.xlsx               # 📊 SAMPLE EXCEL
│
├── templates/                      # 📝 TAG TEMPLATES
│   └── fb_pageview.html
│
├── config/                         # 🔑 CREDENTIALS
│   └── service_account.json        # Google Service Account
│
└── tests/                          # 🧪 UNIT TESTS
    ├── test_gtm_client.py
    ├── test_parser.py
    └── test_schema.py
```

---

## 🔄 Detailed Execution Flow

### **Phase 1: Initialization**
```
1. User runs: python app.py --input data.json
2. app.py loads .env configuration
3. Validate: GTM_ACCOUNT_ID, GTM_CONTAINER_ID, SERVICE_ACCOUNT_JSON_PATH
4. Initialize logger (utils.setup_logging())
5. Check service_account.json exists
```

### **Phase 2: File Processing**
```
6. parser.parse_file(data.json)
   ├─ Detect file type (.json or .xlsx)
   ├─ Parse content
   └─ Return: {variables: [], triggers: [], tags: []}

7. schema.validate_input_data(parsed_data)
   ├─ Check JSON schema compliance
   ├─ Validate required fields
   └─ Raise error if invalid
```

### **Phase 3: GTM Authentication**
```
8. gtm_client = GTMClient(service_account.json, account_id, container_id)
   ├─ Load credentials
   ├─ Authenticate with OAuth 2.0
   └─ Build GTM API service object
```

### **Phase 4: Workspace Creation**
```
9. workspace = gtm_client.create_workspace("AutoGen_20251210_143025")
   ├─ API: POST /accounts/{id}/containers/{id}/workspaces
   ├─ Store workspace_id
   └─ Log success
```

### **Phase 5: Resource Creation**
```
10. CREATE VARIABLES
    FOR variable in parsed_data['variables']:
        gtm_client.create_variable(variable)
        ├─ API: POST /workspaces/{id}/variables
        └─ Log: "Variable created: {name}"

11. CREATE TRIGGERS (Store ID mapping)
    trigger_id_map = {}
    FOR trigger in parsed_data['triggers']:
        created_trigger = gtm_client.create_trigger(trigger)
        trigger_id_map[trigger['name']] = created_trigger['triggerId']
        └─ Log: "Trigger created: {name} (ID: {id})"

12. CREATE TAGS (Link triggers)
    FOR tag in parsed_data['tags']:
        # Map trigger names to IDs
        tag['firingTriggerId'] = [trigger_id_map[name] for name in tag['firing_triggers']]
        gtm_client.create_tag(tag, trigger_id_map)
        └─ Log: "Tag created: {name}"
```

### **Phase 6: Completion**
```
13. Generate summary report
    ├─ Total resources created
    ├─ Workspace URL
    └─ Status (SUCCESS/FAILED)

14. Log summary to console
15. Send notification (optional)
16. Exit with status code
```

---

## 🔑 Key Decision Points

| **Step** | **Decision** | **Action** |
|----------|--------------|------------|
| File Type | JSON or Excel? | Auto-detect by extension |
| Validation | Schema valid? | FAIL FAST if invalid |
| Authentication | Credentials OK? | Raise error if failed |
| Workspace | Name conflict? | Always create NEW with timestamp |
| Variables | Creation fails? | Log error, CONTINUE to next |
| Triggers | Creation fails? | Log error, CONTINUE to next |
| Tags | Trigger not found? | Log warning, skip trigger reference |
| Completion | All successful? | Return SUCCESS status |

---

## 📊 Input Data Format

### **JSON Structure:**
```json
{
  "variables": [
    {
      "name": "Page URL",
      "type": "u",
      "parameter": [{"key": "component", "value": "URL", "type": "template"}]
    }
  ],
  "triggers": [
    {
      "name": "All Pages",
      "type": "PAGEVIEW"
    },
    {
      "name": "Click Button",
      "type": "CLICK",
      "autoEventFilter": [...]
    }
  ],
  "tags": [
    {
      "name": "GA4 Pageview",
      "type": "gaawe",
      "parameter": [...],
      "firingTriggerId": ["All Pages"]
    }
  ]
}
```

### **Excel Structure:**

**Sheet 1: Variables**
| name | type | value | parameter_key | parameter_value |
|------|------|-------|---------------|-----------------|
| Page URL | u | | component | URL |

**Sheet 2: Triggers**
| name | type | event_name | filter_type | filter_parameter |
|------|------|------------|-------------|------------------|
| All Pages | PAGEVIEW | | | |
| Purchase Event | CUSTOM_EVENT | purchase | | |

**Sheet 3: Tags**
| name | type | html | firing_triggers | parameter_key | parameter_value |
|------|------|------|-----------------|---------------|-----------------|
| FB Pixel | html | <script>...</script> | All Pages | | |

---

## 🚀 Execution Command

```bash
# Basic usage
python app.py --input sample_input.json

# With custom workspace name
python app.py --input data.xlsx --workspace "Black Friday Tags"

# Verbose logging
python app.py --input data.json --verbose

# Dry run (validation only)
python app.py --input data.json --dry-run
```

---

## ✅ Success Criteria

✔️ Workspace created with unique name  
✔️ All variables created successfully  
✔️ All triggers created and ID-mapped  
✔️ All tags created with correct trigger links  
✔️ No manual intervention needed  
✔️ Team can directly "Submit" in GTM UI  

---

## 🎯 End Result

```
╔═══════════════════════════════════════════════════════════╗
║              AUTOMATION COMPLETE ✓                         ║
╠═══════════════════════════════════════════════════════════╣
║  Workspace: AutoGen_20251210_143025                        ║
║  Variables Created: 5                                      ║
║  Triggers Created: 8                                       ║
║  Tags Created: 12                                          ║
║                                                            ║
║  🔗 Open GTM: https://tagmanager.google.com/#/...          ║
║                                                            ║
║  ➡️  Next Step: Review and click "Submit" button           ║
╚═══════════════════════════════════════════════════════════╝
```

Business team opens GTM → sees fully configured workspace → clicks Submit → Done! 🎉
