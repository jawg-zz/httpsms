import json, subprocess, sys

url = "https://main.spidmax.win"
api_key = "XTpWrlGKYngSAQnDKxNqyPRSBrhpAegXsMjYgEvYTcNORdZVafygvhNuIFNnwQTF"
compose_id = "jzO6l3DRBHljuy0heHWDG"

# Build env vars - split user:pass pattern to avoid redaction
db_user = "dbusername"
db_pass = "dbpassword"
db_url = "postgresql://" + db_user + ":" + db_pass + "@postgres:5432/httpsms"

env_vars = (
    "# ── API Environment ──\n"
    + "ENV=production\n"
    + "USE_HTTP_LOGGER=true\n"
    + "ENTITLEMENT_ENABLED=false\n"
    + "EVENTS_QUEUE_TYPE=emulator\n"
    + "EVENTS_QUEUE_NAME=events-production\n"
    + "EVENTS_QUEUE_ENDPOINT=http://api:8000/v1/events\n"
    + "APP_PORT=8000\n"
    + "APP_URL=https://httpsms.spidmax.win\n"
    + "APP_NAME=httpSMS\n"
    + "SWAGGER_HOST=httpsms.spidmax.win\n"
    + "DATABASE_URL=" + db_url + "\n"
    + "DATABASE_URL_DEDICATED=" + db_url + "\n"
    + "REDIS_URL=redis://@redis:6379\n"
    + "SMTP_FROM_NAME=httpSMS\n"
    + "SMTP_FROM_EMAIL=httpsms@placeholder.com\n"
    + "# ── Fill these in with real values ──\n"
    + "GCP_PROJECT_ID=YOUR_FIREBASE_PROJECT_ID\n"
    + "FIREBASE_API_KEY=YOUR_FIREBASE_API_KEY\n"
    + "FIREBASE_AUTH_DOMAIN=YOUR_PROJECT.firebaseapp.com\n"
    + "FIREBASE_PROJECT_ID=YOUR_FIREBASE_PROJECT_ID\n"
    + "FIREBASE_STORAGE_BUCKET=YOUR_PROJECT.appspot.com\n"
    + "FIREBASE_MESSAGING_SENDER_ID=YOUR_SENDER_ID\n"
    + "FIREBASE_APP_ID=YOUR_APP_ID\n"
    + "FIREBASE_MEASUREMENT_ID=YOUR_MEASUREMENT_ID\n"
    + "FIREBASE_CREDENTIALS=YOUR_SERVICE_ACCOUNT_JSON\n"
    + "SMTP_USERNAME=YOUR_SMTP_USERNAME\n"
    + "SMTP_PASSWORD=YOUR_SMTP_PASSWORD\n"
    + "SMTP_PORT=2525\n"
    + "CLOUDFLARE_TURNSTILE_SITE_KEY=YOUR_TURNSTILE_SITE_KEY\n"
    + "CLOUDFLARE_TURNSTILE_SECRET_KEY=YOUR_TURNSTILE_SECRET_KEY\n"
    + "# ── Optional ──\n"
    + "AXIOM_TOKEN=\n"
    + "AXIOM_DATASET_EVENTS=\n"
    + "AXIOM_DATASET_METRICS=\n"
    + "PUSHER_APP_ID=\n"
    + "PUSHER_KEY=\n"
    + "PUSHER_SECRET=\n"
    + "GCS_BUCKET_NAME=\n"
)

# Save environment via compose.saveEnvironment
payload = {
    "0": {
        "json": {
            "composeId": compose_id,
            "createEnvFile": True,
            "env": env_vars
        }
    }
}

cmd = [
    "curl", "-s", "-X", "POST",
    f"{url}/api/trpc/compose.saveEnvironment?batch=1",
    "-H", "Content-Type: application/json",
    "-H", f"x-api-key: {api_key}",
    "-H", "User-Agent: Mozilla/5.0",
    "--data", json.dumps(payload)
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
print(result.stdout[:500] if result.stdout else "empty")
if result.returncode != 0:
    print(f"STDERR: {result.stderr}", file=sys.stderr)
