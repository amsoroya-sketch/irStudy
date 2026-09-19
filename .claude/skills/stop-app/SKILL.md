---
description: |
  Stop the locally-running irStudy app processes: FastAPI backend (:8001) and Vite frontend (:5173).
  Leaves the Docker infra (Postgres/Redis/Qdrant) running by default. Use when asked to stop,
  kill, or shut down the app after running it.
allowed-tools:
  - Bash
user-invocable: true
effort: low
---

# Stop the irStudy app

Kills the app processes started by `/run-app` (or `start_all_services.sh`). Counterpart to
[run-app](../run-app/SKILL.md).

## Stop app processes (leave infra up)
```bash
pkill -f 'venv/bin/uvicorn src.main:app' || echo "no backend running"
pkill -f 'vite' || echo "no frontend running"
```
Verify they're down (expect `000`):
```bash
curl -s -o /dev/null -w 'backend:%{http_code}\n' http://localhost:8001/health
curl -s -o /dev/null -w 'frontend:%{http_code}\n' http://localhost:5173/
```

## Also stop the Docker infra (full shutdown)
Only when explicitly asked to tear everything down — other work may rely on Postgres/Redis/Qdrant:
```bash
cd /home/dev/Development/irStudy && docker compose down
```
Or use the repo's `./stop_all_services.sh`, which does both app + `docker compose down`.

## Notes
- `pkill -f 'vite'` matches any Vite process — harmless here (this is the only Vite app), but be
  aware if you run multiple Vite projects.
- The Docker containers (`irstudy-postgres`, `irstudy-redis`, `irstudy-qdrant`) are shared infra;
  prefer leaving them up between runs.
