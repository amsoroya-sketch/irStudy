---
description: |
  Launch and drive the full irStudy stack locally: FastAPI backend (:8001) + Vite/React
  frontend (:5173), against the Docker infra (Postgres :5433, Redis :6380, Qdrant :6333).
  Use when asked to run/start the app, smoke-test it, or confirm a change works in the real app.
allowed-tools:
  - Read
  - Bash
  - Grep
user-invocable: true
effort: medium
---

# Run the irStudy app (full stack)

Verified working 2026-09-20. This is the **authoritative** launch recipe — prefer it over
the root `start_all_services.sh`, which is stale (wrong ports 8000/5174, wrong `venv`).

## Critical gotchas (why the obvious commands fail)

1. **Backend MUST run via the venv uvicorn, not the global one.**
   `backend/start-backend.sh` calls bare `uvicorn`, which resolves off `$PATH` to the global
   Python that is **missing `prometheus_client`** → `ModuleNotFoundError` on boot.
   Always use `backend/venv/bin/uvicorn`.
2. **Backend MUST be pinned to `--port 8001`.**
   The frontend hardcodes `http://localhost:8001/api/v1` (`frontend/src/utils/axiosInstance.ts`,
   `frontend/src/api/client.ts`). The `.env`/`main.py` default is 8000, which is also occupied
   by an unrelated `ideas-backend` container. Pin 8001 explicitly.
3. **Frontend serves on 5173** (Vite default), not 5174 as the old script claims.
4. Env comes from `backend/.env` (DB password, JWT secret, ANTHROPIC_API_KEY, CORS).

## Steps

### 0. Ensure Docker infra is up (usually already running)
```bash
docker ps --format '{{.Names}}\t{{.Status}}' | grep irstudy
```
Expect `irstudy-postgres` (healthy, :5433), `irstudy-redis` (:6380), `irstudy-qdrant` (:6333).
If missing, bring them up:
```bash
cd /home/dev/Development/irStudy && docker compose up -d postgres redis qdrant
```

### 1. Start the backend (port 8001, venv uvicorn)
Run in background; logs to scratchpad.
```bash
cd /home/dev/Development/irStudy/backend
export $(grep -v '^#' .env | xargs)
venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8001
```
Wait for health:
```bash
curl -s http://localhost:8001/health    # -> {"status":"healthy",...}
```
Note: `/api/v1/health` is **404** — the health route is `/health`. Docs live at `/api/docs`.

### 2. Start the frontend (Vite, port 5173)
```bash
cd /home/dev/Development/irStudy/frontend
npm run dev        # -> Local: http://localhost:5173/
```
(If `node_modules` is absent, `npm install` first.)

### 3. Drive it — don't just launch it
Unauthenticated `/` redirects to `/login`. Verify the login page actually renders (a blank
frame = failed launch). Use Playwright from **inside** `frontend/` so `@playwright/test` resolves:
```bash
cd /home/dev/Development/irStudy/frontend
cat > _shot.mjs <<'EOF'
import { chromium } from '@playwright/test';
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
const pe=[]; p.on('pageerror', e=>pe.push(e.message));
await p.goto('http://localhost:5173/login', { waitUntil: 'networkidle' });
await p.waitForTimeout(2000);
console.log('URL', p.url(), '#root len', (await p.innerHTML('#root')).length);
await p.screenshot({ path: process.env.SS });
if (pe.length) console.log('PAGE_ERRORS:\n'+pe.join('\n'));
await b.close();
EOF
SS=/tmp/login.png node _shot.mjs; rm -f _shot.mjs
```
Then **look at the screenshot**. Expect the "irStudy — Medical Education Platform" card with
Email/Password fields and a Sign In button, no console/page errors.

## Stop
```bash
pkill -f 'venv/bin/uvicorn src.main:app'   # backend
pkill -f 'vite'                            # frontend
```
Leave the Docker infra running unless asked to stop it.
