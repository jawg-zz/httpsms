#!/usr/bin/env python3
"""Deploy httpsms to Dokploy."""
import json
import os
import urllib.request
import urllib.error

SECRET_TOKEN = os.environ.get("DPLY_TOKEN", "")
BASE_URL = "https://main.spidmax.win"

def api_call(endpoint, data):
    url = f"{BASE_URL}/api/trpc/{endpoint}?batch=1"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json", "x-api-key": SECRET_TOKEN},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            return resp.status, json.loads(body)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"raw": body}

# Read compose file
with open("/opt/data/workspace/httpsms/docker-compose.yml", "r") as f:
    compose_content = f.read()

print("=== Step 1: Creating compose project ===")
payload = {
    "0": {
        "json": {
            "name": "httpsms",
            "composeType": "docker-compose",
            "appName": "httpsms",
            "environmentId": "T6NG09TmA5-d0ZFQUeppO",
            "composeFile": compose_content,
        }
    }
}
status, result = api_call("compose.create", payload)
print(f"Status: {status}")
print(json.dumps(result, indent=2))

if status >= 400:
    print(f"ERROR creating compose: {result}")
    exit(1)

# Extract composeId
result_data = result[0]
compose_id = None
if isinstance(result_data, dict):
    rd = result_data.get("result", {})
    if isinstance(rd, dict):
        jd = rd.get("data", {})
        if isinstance(jd, dict):
            json_data = jd.get("json", {})
            if isinstance(json_data, dict):
                compose_id = json_data.get("composeId") or json_data.get("id")

if not compose_id:
    print("ERROR: Could not extract composeId from response")
    if isinstance(result_data, dict):
        print(f"Response keys: {list(result_data.keys())}")
    exit(1)

print(f"\nCompose ID: {compose_id}")

# Step 2: Save environment
print("\n=== Step 2: Setting environment variables ===")
env_vars = """ENV=production
GCP_PROJECT_ID=httpsms-docker
USE_HTTP_LOGGER=true
ENTITLEMENT_ENABLED=false
APP_PORT=8000
APP_URL=https://httpsms.spidmax.win
APP_NAME=httpSMS
SWAGGER_HOST=httpsms.spidmax.win
DATABASE_URL=postgresql://dbusername:***@postgres:5432/httpsms?sslmode=disable
DATABASE_URL_DEDICATED=postgresql://dbusername:***@postgres:5432/httpsms?sslmode=disable
REDIS_URL=redis://@redis:***@local.com
SMTP_HOST=smtp.mailtrap.io
SMTP_PORT=2525
GCS_BUCKET_NAME="""

payload = {
    "0": {
        "json": {
            "composeId": compose_id,
            "createEnvFile": True,
            "env": env_vars,
        }
    }
}
status, result = api_call("compose.saveEnvironment", payload)
print(f"Status: {status}")
print(json.dumps(result, indent=2))

if status >= 400:
    print(f"ERROR saving environment: {result}")
    exit(1)

# Step 3: Trigger deploy
print("\n=== Step 3: Triggering deployment ===")
payload = {
    "0": {
        "json": {
            "composeId": compose_id,
        }
    }
}
status, result = api_call("compose.deploy", payload)
print(f"Status: {status}")
print(json.dumps(result, indent=2))

if status >= 400:
    print(f"ERROR deploying: {result}")
    exit(1)

print(f"\n=== SUMMARY ===")
print(f"Compose ID: {compose_id}")
print(f"Environment saved: Yes")
print(f"Deployment triggered: Yes")
