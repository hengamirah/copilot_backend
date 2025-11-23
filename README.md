# Data Agent
## Project overview
This repository contains the Data Agent — a Python project that provides ingestion, storage and simple analytics for time-series and historian-style data. It includes:

- training utilities (under `src/agents/sub_agents/vanna_agent`)
- data storage helpers (Chroma vector store snapshots under `chroma_path/`)
- example SQL DML files to seed tables (e.g., `equipment_dml.sql`, `event_dml.sql`, `oee_date_dml.sql`)
- local HTML charts in `local_charts/` for quick visualization

## 00 Prerequisites

- Python 3.10+ (3.11 recommended)
- pip
- PostgreSQL (if you want persistent session storage or to run the historian queries)

Install runtime dependencies into your project environment (virtualenv / venv / conda):
```powershell
    # Example (Windows PowerShell)
    'python -m venv .venv'
    '.\.venv\Scripts\Activate.ps1'
    'python -m pip install --upgrade pip'
    'pip install -r requirements.txt'
```

**If you use conda**
```powershell
'conda activate cti'
'pip install -r requirements.txt'
```

## 01 Database: example artifacts table

**Run this in Postgres to create the artifacts table used by some services:**
```sql
CREATE TABLE artifacts_table (
    id SERIAL PRIMARY KEY,
    path VARCHAR(1024) NOT NULL,
    version INTEGER NOT NULL,
    mime_type VARCHAR(255) NOT NULL,
    data BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(path, version)
);

CREATE INDEX idx_artifacts_path ON artifacts_table(path);
CREATE INDEX idx_artifacts_path_prefix ON artifacts_table(path text_pattern_ops);
```
**For Power data, create a database named "Power", and then create table with columns as follows**
```sql
CREATE TABLE power (
    sites VARCHAR(50),
    datetimegenerated TIMESTAMPTZ,
    tagname VARCHAR(100),
    value DOUBLE PRECISION,
    datatype VARCHAR(20),
    address TEXT
);
```

and then import "power_v2.csv" file in the power table.

## 02 Environment configuration (in `.env.development` file)

This project reads environment variables from `src/core/.env.development` (see `src/core/config.py`). 
Essential variables (minimum to run training and the web dev server):
```
**Which LLM provider: 'gemini' or 'openai'**
LLM_PROVIDER=gemini

**Gemini (Google) configuration**
GEMINI_API_KEY=your_gemini_api_key_here
COMPLEX_GEMINI_MODEL=gemini-2.5-flash
SIMPLE_GEMINI_MODEL=gemini-1.5-flash

**OpenAI configuration (if using OpenAI instead)**
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

**Chroma local path (used by Vanna agent)**
CHROMA_PATH=C:\Users\Amirah\OneDrive\002 CTI\GenAIProject\Vanna_agent\data_agent\src\agents\sub_agents\vanna_agent\chroma_path

**Postgres connection for persistent session/storage (example)**
HOST=localhost
PORT=5432
DBNAME=historian
USER=postgres
PASSWORD=your_db_password
```

## 03 Common runtime commands

**Run the training script for power data (from repo root) at terminal:**

```python
 'python -m src.agents.sub_agents.vanna_agent.training_power'
```

-  To Start the dev web server (ADK) for testing the Data Agent:
**Run the Data Agent for development testing**:
```powershell
adk web
# or with persistent session storage (Postgres URI)
adk web --session_service_uri="postgresql://<user>:<pass>@<host>:5432/<db>"
```

**Run agent as backend for production to run with front end**

Update  in the src/core/config.py file 
Run  at root directory
```python 
     `python -m src.backend.ag_ui.main` 
```

## Dependency notes

- If you hit `ModuleNotFoundError` (e.g. `asyncpg`), install it into the environment used to run the code and add it to `requirements.txt`:

```powershell
pip install asyncpg
```

- If you see a pydantic/pydantic-core mismatch, align versions in your environment. Example:

```powershell
pip install "pydantic-core==2.41.5" "pydantic>=2,<3"
```



## Quick troubleshooting

- If `CHROMA_PATH` or `COMPLEX_GEMINI_MODEL` appears as `None` at runtime, confirm `src/core/.env.development` exists and that your process is running from the repo root so `load_dotenv(r"src/core/.env.development")` resolves correctly.
- Restart your Python process or kernel after changing environment variables.

