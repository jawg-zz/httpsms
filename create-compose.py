import json, subprocess, sys

# Read the compose file from the local repo
with open("/opt/data/workspace/httpsms/docker-compose.yml") as f:
    compose_content = f.read()

# Dokploy API details
url = "https://main.spidmax.win"
api_key = "XTpWrlGKYngSAQnDKxNqyPRSBrhpAegXsMjYgEvYTcNORdZVafygvhNuIFNnwQTF"
env_id = "T6NG09TmA5-d0ZFQUeppO"

# Build the tRPC payload
payload = {
    "0": {
        "json": {
            "name": "httpsms",
            "description": "Self-hosted SMS gateway - Android phone to HTTP API",
            "environmentId": env_id,
            "composeType": "docker-compose",
            "appName": "httpsms",
            "composeFile": compose_content
        }
    }
}

# Make the request using curl via subprocess (bypasses Python urllib Cloudflare issues)
cmd = [
    "curl", "-s", "-X", "POST",
    f"{url}/api/trpc/compose.create?batch=1",
    "-H", "Content-Type: application/json",
    "-H", f"x-api-key: {api_key}",
    "-H", "User-Agent: Mozilla/5.0",
    "--data", json.dumps(payload)
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
print(result.stdout)

if result.returncode != 0:
    print(f"STDERR: {result.stderr}", file=sys.stderr)
