# Evaluation System - Quick Reference Card

**Single-page reference for common tasks**

---

## 🚀 Getting Started (5 Minutes)

```bash
# 1. Start Vault
docker compose -f docker-compose.dev.yml up -d vault

# 2. Store API key
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='dev-only-token-change-in-prod'
./evaluation-system/scripts/setup_vault_api_key.sh YOUR_ANTHROPIC_API_KEY

# 3. Test
source venv/bin/activate
venv/bin/python3 evaluation-system/scripts/test_single_item.py
```

---

## 📊 System Status

```bash
# Check infrastructure
ls -1 .claude/agents/*.md | wc -l  # Expected: 13 agents
jq '.statistics.total_items' evaluation-system/data/knowledge_item_registry.json  # Expected: 3170

# Check Vault
vault status  # Expected: Sealed=false
vault kv get secret/ai-osce/claude-api-key  # Expected: Key present

# Check services
docker ps | grep -E "vault|qdrant|postgres|redis"
```

---

## 🏃 Common Tasks

### **Test Single Item**

```bash
venv/bin/python3 evaluation-system/scripts/test_single_item.py
# Expected: ✅ Score: 8.5/10, Status: PASS (30-60 seconds)
```

### **Test 10 Items**

```bash
venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py \
  --max-items 10 \
  --output-dir evaluation-system/reports/test_10_items
# Expected: 10 evaluations in ~10 minutes
```

### **Production Run (All 2,963 Items)**

```bash
venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py \
  --batch-size 5 \
  --max-parallel-agents 10 \
  --batch-delay 2 \
  --output-dir evaluation-system/reports/production_iteration_1
# Expected: 6-8 hours, 2,963 evaluations
```

### **Check Progress**

```bash
# Real-time monitoring
tail -f evaluation-system/logs/production_run_*.log

# Statistics
jq '.statistics' evaluation-system/reports/production_iteration_1/summary.json
# Shows: total_items, evaluated, progress_percent, avg_score, approval_rate
```

---

## 📁 Key Files

| File | Location | Purpose |
|------|----------|---------|
| **Orchestrator** | `core/evaluation_orchestrator.py` | Main evaluation engine |
| **Delegation** | `core/claude_task_delegation.py` | Vault + API integration |
| **Registry** | `data/knowledge_item_registry.json` | 3,170 items catalogue |
| **Rules** | `config/agent_assignment_rules.yaml` | Assignment logic |
| **Prompts** | `config/evaluation_prompts/*.md` | 13 evaluation templates |
| **Agents** | `.claude/agents/*.md` | 13 expert agents |

---

## 🐛 Troubleshooting

### **Vault Connection Failed**

```bash
# Start Vault
docker compose -f docker-compose.dev.yml up -d vault

# Check status
export VAULT_ADDR='http://127.0.0.1:8200'
vault status  # Should show: Sealed=false
```

### **API Key Not Found**

```bash
# Store API key
export VAULT_TOKEN='dev-only-token-change-in-prod'
vault kv put secret/ai-osce/claude-api-key value="YOUR_KEY"

# Verify
vault kv get secret/ai-osce/claude-api-key
```

### **JSON Parse Error**

```bash
# The system has automatic retry logic (max 2 retries)
# If persistent, check logs:
cat evaluation-system/logs/production_run_*.log | grep "JSONParseError"
```

### **Rate Limiting**

```bash
# Increase delay between batches
venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py \
  --batch-delay 5  # Increase from 2 to 5 seconds
```

---

## 📈 Expected Performance

| Metric | Iteration 1 | Iteration 2 | Iteration 3 (Final) |
|--------|-------------|-------------|---------------------|
| **Avg Score** | 7.2-7.8 | 8.6-8.9 | **9.4-9.7** |
| **Approval Rate** | 65-75% | 89-92% | **99%+** |
| **Violations** | ~234 | ~23 | **0** |
| **Duration** | 6-8 hours | 4-5 hours | 2-3 hours |

---

## 📖 Full Documentation

- **Primary reference:** [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)
- **System overview:** [FINAL_SYSTEM_SUMMARY.md](FINAL_SYSTEM_SUMMARY.md)
- **Quick start:** [README.md](README.md)

---

## ✅ Pre-Flight Checklist

- [ ] Vault running (`docker ps | grep vault`)
- [ ] API key stored (`vault kv get secret/ai-osce/claude-api-key`)
- [ ] Virtual env activated (`source venv/bin/activate`)
- [ ] Single item test passed (`test_single_item.py`)
- [ ] 10-item test passed (`--max-items 10`)
- [ ] Ready for production run

---

**Status:** ✅ **PRODUCTION READY**
**Questions?** See [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md) for complete instructions
