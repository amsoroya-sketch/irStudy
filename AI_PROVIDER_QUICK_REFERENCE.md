# AI Provider Quick Reference

Quick commands to switch between Kimi (FREE) and Claude (PAID) for AI validation.

---

## Current Setup

Check which AI provider is active:

```bash
cd /home/dev/Development/irStudy/backend
grep AI_PROVIDER .env
```

---

## Switch to Kimi (FREE) ⭐

```bash
cd /home/dev/Development/irStudy/backend

# Edit .env
nano .env

# Set these values:
AI_PROVIDER=kimi
KIMI_API_KEY=sk-your-kimi-api-key

# Restart backend
docker-compose restart backend

# Verify
curl http://localhost:8001/api/v1/ai-validation/health
```

**Expected**: `"provider": "kimi"`, `"cost": "FREE"`

---

## Switch to Claude (PAID)

```bash
cd /home/dev/Development/irStudy/backend

# Edit .env
nano .env

# Set these values:
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-claude-key

# Restart backend
docker-compose restart backend

# Verify
curl http://localhost:8001/api/v1/ai-validation/health
```

**Expected**: `"provider": "claude"`, `"cost": "PAID"`

---

## Quick Test

```bash
# Test validation endpoint
curl -X POST http://localhost:8001/api/v1/ai-validation/validate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "soap",
    "data": {
      "subjective": {"chiefComplaint": "Test", "hpi": "Test patient with test symptoms for testing purposes only."},
      "objective": {"vitalSigns": {"temperature": 37, "heartRate": 75, "bloodPressureSystolic": 120, "bloodPressureDiastolic": 80, "respiratoryRate": 16, "oxygenSaturation": 98}},
      "assessment": {"primaryDiagnosis": "Test diagnosis", "clinicalReasoning": "Test reasoning for educational purposes only."},
      "plan": {"investigations": "Test investigations", "followUp": "Test follow-up plan"}
    }
  }' | jq '.ai_provider'
```

**Returns**: `"kimi"` or `"claude"`

---

## Comparison

| Feature | Kimi | Claude |
|---------|------|--------|
| **Cost** | FREE ✅ | $3-15 per 1M tokens |
| **Quality** | Good (85%) | Excellent (95%) |
| **Speed** | 3-5s | 3-5s |
| **Context** | 128K tokens | 200K tokens |
| **Privacy** | China-based | US-based (HIPAA) |
| **Best For** | Practice/Education | Production |

---

## File Locations

**Config**: `/home/dev/Development/irStudy/backend/.env`

**Kimi Adapter**: `/home/dev/Development/irStudy/backend/src/ai_router/kimi_adapter.py`

**Validator (Kimi)**: `/home/dev/Development/irStudy/backend/src/validators/ai_validator_kimi.py`

**Validator (Claude)**: `/home/dev/Development/irStudy/backend/src/validators/ai_validator.py`

**API Router**: `/home/dev/Development/irStudy/backend/src/api/v1/ai_validation_router.py`

---

## Troubleshooting

### "Provider not available"

```bash
# Check environment variables are loaded
docker-compose exec backend env | grep -E "(KIMI|ANTHROPIC|AI_PROVIDER)"

# Restart to reload .env
docker-compose down
docker-compose up -d
```

### "API key invalid"

**Kimi**:
- Get new key: https://platform.moonshot.cn/
- Format: `sk-...` (starts with `sk-`)

**Claude**:
- Get key: https://console.anthropic.com/
- Format: `sk-ant-...` (starts with `sk-ant-`)

### JSON parsing errors (Kimi)

Kimi sometimes adds explanation text. The adapter handles this, but if issues persist:

```python
# In ai_validator_kimi.py, add more explicit instruction:
prompt += "\n\nCRITICAL: Return ONLY the JSON object with no additional text before or after."
```

---

## Environment Variables

```bash
# Kimi (FREE)
AI_PROVIDER=kimi
KIMI_API_KEY=sk-...
KIMI_BASE_URL=https://api.moonshot.cn/v1

# Claude (PAID)
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-...
```

---

**Recommendation**: Start with **Kimi (FREE)** for development and testing, switch to **Claude** only if needed for production or higher quality.
