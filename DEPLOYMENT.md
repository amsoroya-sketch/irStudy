# irStudy — External Deployment Guide

How to make irStudy reachable from the internet. Two paths:

- **Path A — Student access TODAY** (Cloudflare quick tunnel from your machine). Minutes to set up; your machine must stay on. Stopgap.
- **Path B — Durable VPS** (your existing Docker Compose stack behind Caddy with a real domain + auto‑HTTPS). The real thing.

Both paths use the **same** containers and the **same** origin‑relative frontend build, so nothing is throwaway except the tunnel itself.

## What makes this work (architecture)

- **Caddy** is the only internet‑facing service. It serves the built React SPA and reverse‑proxies `/api/*` and `/ws/*` to the FastAPI backend on the internal Docker network. WebSockets upgrade automatically.
- The frontend uses **origin‑relative URLs** (`/api/v1`, and `wss://<current-host>/ws/...`), so one build works behind the tunnel hostname *and* the real domain with no rebuild. (`frontend/.env.production`, `src/utils/axiosInstance.ts`, `src/api/client.ts`, `src/components/osce/WebSocketChat.tsx`.)
- In `docker-compose.yml`, every service is published to **`127.0.0.1` only**. The production overlay (`docker-compose.prod.yml`) adds Caddy publishing `80/443` to the world. Result: Postgres/Redis/Qdrant/Neo4j/Adminer/Flower/Grafana are never exposed on the public IP.
- Auth is already enforced (JWT). `ENV=production` turns on `TrustedHostMiddleware`; the host allowlist is env‑driven (`ALLOWED_HOSTS`).

> **Frontend build note:** the repo has pre‑existing TypeScript errors, so `npm run build` (which runs `tsc -b` first) currently fails. The Caddy image builds with `npx vite build` (esbuild, no typecheck), which works. Fixing the type errors is tracked separately.

---

## Path A — Give a student access today (tunnel)

```bash
cd /home/dev/Development/irStudy

# 1. Secrets already exist in secrets/. (If not: `python setup_secrets.py`.)
#    Put your real Anthropic key in secrets/anthropic_api_key.txt (it ships as a placeholder).

# 2. Bring up the production-style stack locally (Caddy on :80, ALLOWED_HOSTS=*).
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 3. Create the student's account (VERIFIED — self-registration stays locked out).
export DATABASE_URL="postgresql://postgres:$(cat secrets/db_password.txt)@localhost:5433/irstudy_medical"
python scripts/create_account.py --email student@example.com \
    --password 'Str0ng!Passphrase' --name "Student Name" --role student
# (make yourself an admin too: --email you@example.com --role admin)

# 4. Open the tunnel and share the printed https://*.trycloudflare.com URL.
scripts/tunnel_now.sh
```

Defaults (`SITE_ADDRESS=:80`, `ALLOWED_HOSTS=*`) already suit a quick tunnel — no `.env` needed for Path A.

---

## Path B — Durable VPS deployment

### 1. Provision
- One Linux VPS, **8–16 GB RAM** (Postgres + Qdrant + Neo4j + Celery reserve a lot). e.g. Hetzner CX32/CX42, DO 8 GB.
- Install Docker Engine + Compose plugin.
- Point a DNS **A record** (e.g. `app.example.com`) at the VPS IP. Open ports **80** and **443** only.

### 2. Get the code + secrets
```bash
git clone <repo> irStudy && cd irStudy
python setup_secrets.py            # generates secrets/*.txt (0600)
# setup_secrets.py does NOT create jwt_secret.txt — create it if missing:
[ -f secrets/jwt_secret.txt ] || (openssl rand -hex 32 > secrets/jwt_secret.txt && chmod 600 secrets/jwt_secret.txt)
# Replace the two placeholder keys with real values:
#   secrets/anthropic_api_key.txt   (required for AI OSCE / content)
#   secrets/openai_api_key.txt      (only if used)
```

### 3. Configure the public address
```bash
cp .env.deploy.example .env
# edit .env:
#   SITE_ADDRESS=app.example.com      # Caddy auto-provisions Let's Encrypt TLS
#   ALLOWED_HOSTS=app.example.com
```

### 4. Launch
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps    # all healthy?
```
Migrations run automatically on backend start (`alembic upgrade head`).

### 5. Create accounts
```bash
export DATABASE_URL="postgresql://postgres:$(cat secrets/db_password.txt)@localhost:5433/irstudy_medical"
python scripts/create_account.py --email you@example.com --password '...' --name "Admin" --role admin
python scripts/create_account.py --email student@example.com --password '...' --name "Student" --role student
```

### 6. Backups (cron on the VPS)
```bash
# nightly Postgres dump into the mounted ./backup volume
0 2 * * *  cd /path/to/irStudy && docker compose exec -T postgres \
  sh -c 'pg_dump -U postgres irstudy_medical' > backup/irstudy_$(date +\%F).sql
# Qdrant snapshot (vectors/RAG)
0 3 * * *  curl -s -X POST http://127.0.0.1:6333/collections/{collection}/snapshots
```
Copy `backup/` and `secrets/` to encrypted off‑box storage.

---

## Verification (run after either path)

Replace `$URL` with the tunnel URL or `https://app.example.com`.

```bash
curl -I  "$URL/"                              # 200, valid TLS (Path B)
curl -s  "$URL/api/docs" -o /dev/null -w '%{http_code}\n'   # 200 (API reachable via proxy)
curl -s  "$URL/api/v1/patient-personas" -o /dev/null -w '%{http_code}\n'  # 401 (auth enforced)
```
In a browser:
- Log in as the student → protected pages load.
- Start an OSCE session → **WebSocket connects over `wss://`** (DevTools → Network → WS).
- PWA installs (needs HTTPS — Path B or the tunnel’s HTTPS).

From **outside** the VPS, confirm nothing but 80/443 is open:
```bash
for p in 5433 6333 6380 7474 8001 8080 3001 5556 9090; do
  timeout 3 bash -c "</dev/tcp/<VPS_IP>/$p" 2>/dev/null && echo "OPEN $p (BAD)" || echo "closed $p"
done
```

---

## Before going FULLY public (Phase 2 — do not skip)

- **Email verification**: implement the `send_verification_email` TODO in `backend/src/api/v1/auth.py`, or keep registration closed and onboard via `scripts/create_account.py`. Right now unverified self‑signups can’t use the app.
- **Rate limiting / lockout**: a limiter and `locked_until` exist — confirm they’re wired on `/auth/login` and tune limits.
- **Legal/PHI**: confirm all patient data is synthetic (personas); add Terms + Privacy. The platform advertises HIPAA‑style controls — document what actually applies.
- **Secrets**: consider moving from flat files to the Vault service (`docker-compose.dev.yml`) for rotation.
- **Observability**: reach Grafana/Prometheus/Adminer via SSH tunnel only (they’re already loopback‑bound); do not publish them.
