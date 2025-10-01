# Vercel Secrets Demo (Python)

Minimal Python serverless function to display Vercel environment variables. Perfect foundation for Odoo API projects.

## Directory Structure

```
vercel-secrets-demo/
├── api/
│   └── index.py          # Python serverless function
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
└── README.md            # This file
```

## Quick Setup

### 1. Create the repo

```bash
mkdir vercel-secrets-demo
cd vercel-secrets-demo
mkdir api

# Copy the files from artifacts:
# - api/index.py
# - requirements.txt
# - vercel.json
# - README.md

git init
git add .
git commit -m "Initial commit: Python Vercel secrets demo"
git remote add origin https://github.com/YOUR_USERNAME/vercel-secrets-demo.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Vercel

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Select your `vercel-secrets-demo` repo
4. Click "Deploy"

### 3. Add Environment Variables in Vercel

In your project settings:
- Go to Settings → Environment Variables
- Add test secrets:
  - `TEST_SECRET_1` = `test_value_one`
  - `DEMO_API_KEY_1` = `demo_key_value`
  - `ODOO_URL` = `https://your-instance.odoo.com`
  - `ODOO_DB` = `your_database`
  - `ODOO_USERNAME` = `admin`
  - `ODOO_API_KEY` = `your_api_key`

### 4. Redeploy

Push a new commit or click "Redeploy" in Vercel dashboard.

Visit your URL to see the secrets displayed.

## How It Works

- Python serverless functions must be in the `api/` folder
- Vercel automatically calls the `handler` class
- Access environment variables via `os.environ`
- Perfect for Odoo API integration using XML-RPC

## Next Step: Odoo Integration

When ready to connect to Odoo, add this to your Python code:

```python
import xmlrpc.client
import os

odoo_url = os.environ.get('ODOO_URL')
odoo_db = os.environ.get('ODOO_DB')
odoo_username = os.environ.get('ODOO_USERNAME')
odoo_api_key = os.environ.get('ODOO_API_KEY')

# Authenticate
common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')
uid = common.authenticate(odoo_db, odoo_username, odoo_api_key, {})

# Access Odoo models
models = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object')
```

## Security Note

This demo displays secrets for learning purposes only. Never expose real API keys to the client in production.