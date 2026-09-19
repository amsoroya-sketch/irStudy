#!/usr/bin/env bash
#
# Expose the local irStudy stack to the internet via a Cloudflare quick tunnel,
# so you can hand a student a working HTTPS URL TODAY (no server, no DNS).
#
# Prereqs:
#   1. Generate secrets once:            python setup_secrets.py   (see DEPLOYMENT.md)
#   2. Bring up the prod-style stack:
#        docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
#      Caddy listens on http://localhost:80 and proxies /api + /ws to the backend.
#      (ALLOWED_HOSTS defaults to "*", so the random tunnel hostname is accepted.)
#   3. Create the student's account (verified):
#        export DATABASE_URL="postgresql://postgres:$(cat secrets/db_password.txt)@localhost:5433/irstudy_medical"
#        python scripts/create_account.py --email student@example.com \
#            --password 'Str0ng!Passphrase' --name "Student Name" --role student
#
# Then run this script. Cloudflare prints a https://<random>.trycloudflare.com
# URL that tunnels to your local Caddy. Share it; Ctrl-C stops the tunnel.
#
# NOTE: this requires YOUR machine to stay on. It's a stopgap until the VPS
# (DEPLOYMENT.md) is live. cloudflared is already installed at /usr/local/bin.
set -euo pipefail

PORT="${1:-80}"

if ! command -v cloudflared >/dev/null 2>&1; then
  echo "❌ cloudflared not found. Install it or use the VPS path in DEPLOYMENT.md." >&2
  exit 1
fi

if ! curl -sf "http://localhost:${PORT}/" >/dev/null 2>&1; then
  echo "⚠️  Nothing responding on http://localhost:${PORT} — is the stack up?" >&2
  echo "    docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build" >&2
fi

echo "🌐 Starting Cloudflare quick tunnel -> http://localhost:${PORT}"
echo "   Share the https://*.trycloudflare.com URL below. Ctrl-C to stop."
exec cloudflared tunnel --url "http://localhost:${PORT}"
