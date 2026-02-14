# Kubernetes Quick Reference for irStudy
## Copy-Paste Guide from NoorBayan

**Location of Source Files:**
```
/home/dev/Development/noorbayan-tree-viewer/
├── k8s/          (14 YAML files - ready to adapt)
└── helm/         (Helm chart - use as reference)
```

---

## One-Page Adaptation Summary

### Files to Copy (Directly or with Minor Changes)

| File | Reusability | Changes Needed | Time |
|------|-------------|---|---|
| namespace.yaml | 95% | Update namespace name | 5 min |
| postgres-statefulset.yaml | 90% | DB name, storage size | 30 min |
| configmap.yaml | 85% | Service URLs, domain | 30 min |
| services.yaml | 90% | Service names if changed | 20 min |
| ingress.yaml | 90% | Domain, cert email | 20 min |
| ingress-local.yaml | 90% | For local k3s dev | 10 min |
| hpa.yaml | 85% | Replica counts | 20 min |
| pdb.yaml | 100% | No changes needed | 0 min |
| networkpolicy.yaml | 80% | Add Redis/Qdrant rules | 1.5 hours |
| secret-template.yaml | 100% | No changes needed | 0 min |

### Files to Create/Adapt

| Component | Source | Effort | Why |
|-----------|--------|--------|-----|
| FastAPI Backend | backend-deployment.yaml | 2.5 hrs | Change Node.js → Python |
| Frontend | frontend-deployment.yaml | 1 hr | Minimal changes (image tag) |
| Celery Workers | python-viz-deployment.yaml | 2 hrs | Similar pattern, add Redis |
| Redis StatefulSet | Copy postgres-statefulset.yaml | 2 hrs | New component |
| Qdrant Vector DB | Copy postgres-statefulset.yaml | 2 hrs | New component |
| Migration Job | migration-job.yaml | 1.5 hrs | Update migration command |

---

## Critical Components Overview

### PostgreSQL (StatefulSet)
```yaml
Purpose: Primary database for MCQs, users, progress
Image: postgres:15-alpine
Storage: 50Gi (adjust per data volume)
Resources: 100m CPU / 512Mi RAM (request), 2000m / 4Gi (limit)
Health: pg_isready
Replicas: 1 (no scaling)
```

### FastAPI Backend
```yaml
Purpose: REST API, business logic, MCQ serving
Image: irstudy/api:v1.0.0
Port: 3001 (change if needed)
Replicas: 2-8 (depends on load)
Health: /health endpoint
HPA: 70% CPU, 80% memory
Dependencies: PostgreSQL, Redis (optional), Qdrant (optional)
```

### Frontend (Next.js/React)
```yaml
Purpose: Web UI for MCQs
Image: irstudy/frontend:v1.0.0
Port: 3000
Replicas: 2-10
Health: GET /
HPA: 70% CPU, 80% memory
Dependencies: Backend API
```

### Celery Workers
```yaml
Purpose: Background tasks, MCQ generation, async operations
Image: irstudy/worker:v1.0.0
Replicas: 2-10
Health: celery inspect ping (or HTTP)
HPA: 75% CPU, 85% memory
Dependencies: Redis (broker), PostgreSQL (state)
```

### Redis (If Needed)
```yaml
Purpose: Caching, session store, Celery broker
Image: redis:7-alpine
Port: 6379
Storage: 10Gi
Replicas: 1 (no scaling)
Health: redis-cli ping
```

### Qdrant Vector Database (If Using)
```yaml
Purpose: Embeddings storage, semantic search
Image: qdrant:latest
Port: 6333
Storage: 20Gi
Replicas: 1 (no scaling)
Health: curl /health
```

---

## Quick Start: Adaptation in 8 Steps

```bash
# Step 1: Clone source files
git clone https://github.com/yourusername/noorbayan-tree-viewer.git
cp -r noorbayan-tree-viewer/k8s irStudy/k8s-configs

# Step 2: Global replacements
cd irStudy/k8s-configs
for file in *.yaml; do
  sed -i 's/noorbayan-prod/irstudy-prod/g' "$file"
  sed -i 's/noorbayan.com/irstudy.med.au/g' "$file"
  sed -i 's|noorbayan/|irstudy/|g' "$file"
done

# Step 3: Create namespace
kubectl apply -f namespace.yaml

# Step 4: Create secrets (MANUALLY - never commit)
kubectl create secret generic postgres-secret \
  --from-literal=password='SECURE_PASSWORD' \
  --namespace irstudy-prod

# Step 5: Create ConfigMap
kubectl apply -f configmap.yaml

# Step 6: Deploy PostgreSQL
kubectl apply -f postgres-statefulset.yaml
kubectl apply -f services.yaml
kubectl wait --for=condition=ready pod/postgres-0 -n irstudy-prod --timeout=300s

# Step 7: Deploy applications
kubectl apply -f api-deployment.yaml  # (adapted from backend)
kubectl apply -f frontend-deployment.yaml
kubectl apply -f celery-deployment.yaml  # (create from template)

# Step 8: Deploy networking & scaling
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml
kubectl apply -f pdb.yaml
kubectl apply -f networkpolicy.yaml

echo "✅ Deployment complete!"
kubectl get all -n irstudy-prod
```

---

## Key Customizations Required

### 1. ConfigMap Changes

**File: configmap.yaml**

From:
```yaml
TREE_SERVER_URL: "http://tree-server:9000"
IIRAB_SERVER_URL: "http://iirab-server:8000"
NEXT_PUBLIC_API_URL: "https://noorbayan.com/api/v1"
```

To:
```yaml
# Remove tree/iirab if not using
# Add new services:
REDIS_URL: "http://redis:6379"
QDRANT_URL: "http://qdrant:6333"
NEXT_PUBLIC_API_URL: "https://irstudy.med.au/api/v1"
```

### 2. Backend Deployment Changes

**File: api-deployment.yaml** (from backend-deployment.yaml)

Change command from:
```yaml
command: ["npm", "run", "start:dev"]
```

To:
```yaml
command: ["gunicorn", "main:app", "--bind", "0.0.0.0:3001"]
# OR uvicorn:
# command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3001"]
```

Add init containers for dependencies:
```yaml
initContainers:
  - name: wait-for-postgres
    image: postgres:15-alpine
    command: [pg_isready -h postgres]
  - name: wait-for-redis
    image: redis:7-alpine
    command: [redis-cli, -h, redis, ping]
```

### 3. Ingress Changes

**File: ingress.yaml**

Update metadata and spec:
```yaml
metadata:
  name: irstudy-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - irstudy.med.au
        - www.irstudy.med.au
      secretName: irstudy-tls
  rules:
    - host: irstudy.med.au
      http:
        paths:
          - path: /api/v1
            backend:
              service:
                name: api  # (if renamed from backend)
```

Update cert-manager email:
```yaml
spec:
  acme:
    email: admin@irstudy.med.au  # Your email
```

### 4. Network Policies

Add rules for new services:

```yaml
---
# Backend to Redis
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-backend-to-redis
  namespace: irstudy-prod
spec:
  podSelector:
    matchLabels:
      app: redis
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api  # (or backend)
    ports:
    - protocol: TCP
      port: 6379

---
# Celery Workers to Redis
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-celery-to-redis
  namespace: irstudy-prod
spec:
  podSelector:
    matchLabels:
      app: redis
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app.kubernetes.io/component: worker
    ports:
    - protocol: TCP
      port: 6379
```

---

## Resource Requirements

### Minimum Cluster for irStudy
```
3 nodes × (4 vCPU, 8GB RAM) = 12 vCPU, 24GB RAM
Storage: 200GB SSD
Network: 100Mbps
```

### Component Resource Allocation
```
PostgreSQL:      100m-2000m CPU, 512Mi-4Gi RAM
FastAPI Backend: 200m-2000m CPU, 512Mi-4Gi RAM (×2-8 replicas)
Frontend:        50m-300m CPU,   64Mi-256Mi RAM (×2-10 replicas)
Celery Workers:  100m-2000m CPU, 256Mi-2Gi RAM (×2-10 replicas)
Redis:           50m-500m CPU,   100Mi-1Gi RAM
Qdrant:          100m-1000m CPU, 256Mi-2Gi RAM
──────────────────────────────────────────────
Total (avg):     ~8 vCPU, 10-15GB RAM required
```

---

## Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Pods stuck in Pending | Check resource availability: `kubectl top nodes` |
| ImagePullBackOff | Push images to registry: `docker push irstudy/api:v1.0.0` |
| CrashLoopBackOff | Check logs: `kubectl logs <pod> --previous` |
| Connection refused | Check service DNS: `kubectl exec <pod> -- nslookup api` |
| Port mismatch | Verify: `kubectl get svc -o wide` matches containers |
| Network policy blocked | Test: `kubectl exec <pod> -- curl service:port` |
| TLS cert issue | Check: `kubectl get certificate` and `kubectl describe cert` |
| HPA not scaling | Verify metrics: `kubectl top pods` shows usage |

---

## Next Steps

1. **Review** the full report: `K8S_EXPLORATION_REPORT.md`
2. **Prepare** your Kubernetes cluster
3. **Adapt** the 14 YAML files for irStudy
4. **Test** in staging environment
5. **Deploy** to production with monitoring
6. **Document** your team's specific setup

---

## Resources Referenced

- **Source:** `/home/dev/Development/noorbayan-tree-viewer/k8s/`
- **Full Report:** `K8S_EXPLORATION_REPORT.md` (2,146 lines)
- **Helm Chart:** `/home/dev/Development/noorbayan-tree-viewer/helm/`
- **Docker Compose Reference:** `/home/dev/Development/noorbayan-tree-viewer/docker-compose.prod.yml`

