# Railway PostgreSQL Database Setup

## Problem
Your server is failing with: `Could not parse SQLAlchemy URL from string ''`

This means the `DATABASE_URL` environment variable is not being set correctly.

## Solution

### 1. Get Your Database Connection String

In Railway:
1. Go to your Postgres service
2. Click on the **Variables** tab
3. Copy the `DATABASE_URL` value (it looks like: `postgresql://user:password@host:port/database`)

### 2. Set Environment Variable in Your Server Service

**Option A: Using Railway Variables (Recommended)**

1. Go to your **Server** service in Railway
2. Click on the **Variables** tab
3. Click **+ New Variable**
4. Add:
   - **Variable Name**: `DATABASE_URL`
   - **Value**: Paste the full connection string from your Postgres service

**Option B: Reference Postgres Service Variable**

1. Go to your **Server** service
2. Click **Variables** tab
3. Click **+ New Variable**
4. Click **Add Reference**
5. Select your Postgres service
6. Select `DATABASE_URL`

### 3. Update Your Code (if needed)

Make sure your `server/app/db/database.py` reads the environment variable:

```python
import os
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
```

### 4. Redeploy

After setting the environment variable:
1. Railway will automatically redeploy your service
2. Or manually trigger a redeploy from the Railway dashboard

### 5. Verify

Check your deployment logs to ensure the connection is successful.

## Common Issues

### Issue: Variable not found
- Make sure you're setting the variable in the **Server** service, not the Postgres service
- The Postgres service already has `DATABASE_URL`, but your server needs it too

### Issue: Still getting empty string
- Ensure you've saved the variable in Railway
- Wait for the automatic redeploy to complete
- Check that your code is reading from `os.getenv("DATABASE_URL")`

### Issue: Connection refused
- Verify the Postgres service is running
- Check that both services are in the same Railway project
- Ensure there are no firewall/network restrictions
