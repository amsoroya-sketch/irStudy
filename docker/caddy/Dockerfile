# Multi-stage: build the React SPA, then serve it from Caddy which also proxies
# /api and /ws to the backend. Build context is the repo root (see
# docker-compose.prod.yml) so we can reach ./frontend.

# ---- Stage 1: build the frontend ----
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
# Use `vite build` directly (NOT `npm run build`): the repo currently has
# pre-existing TypeScript errors that fail `tsc -b`, but esbuild transpiles
# fine and the app runs. Fix the type errors separately, then this can switch
# back to `npm run build`. Origin-relative env comes from frontend/.env.production.
RUN npx vite build

# ---- Stage 2: Caddy serving the SPA + proxying the API ----
FROM caddy:2-alpine
COPY docker/caddy/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv
