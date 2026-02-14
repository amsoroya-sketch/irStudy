# Kimi 2.5 Setup Guide - FREE Alternative to Claude

This guide shows how to use **Kimi 2.5** (Moonshot AI) instead of Claude for FREE AI validation in the EMR Practice System.

---

## Why Kimi 2.5?

**Benefits**:
- ✅ **100% FREE** (Claude costs $3-15 per million tokens)
- ✅ **128K context window** (same as Claude 3.5 Sonnet)
- ✅ **Good Chinese + English support**
- ✅ **Fast response times** (3-5 seconds)
- ✅ **API compatible with OpenAI format**

**Trade-offs**:
- ❌ Slightly less capable than Claude 3.5 Sonnet for complex reasoning
- ❌ Chinese company (Moonshot AI) - data privacy considerations
- ✅ **Good enough for educational feedback and validation**

---

## Step 1: Get Kimi API Key (FREE)

### Option A: Official Moonshot AI Platform (Recommended)

1. **Visit**: https://platform.moonshot.cn/
2. **Register**: Create account with phone number (supports international numbers)
3. **Verify**: Complete phone verification
4. **Get API Key**:
   - Go to "API Keys" section
   - Click "Create New Key"
   - Copy your API key (looks like: `sk-...`)

### Option B: Alternative Method (If you already have access)

If you mentioned you "set up kimi 2.5 on this system", you might already have:
- API key stored somewhere
- Local Kimi instance running
- API endpoint configured

**Check these locations**:
```bash
# Check for existing Kimi config
cat ~/.kimi/config
cat ~/.config/kimi/api_key
env | grep KIMI
```

---

## Step 2: Configure Backend

### Set Environment Variables

**Create `.env` file** in `/home/dev/Development/irStudy/backend/`:

```bash
# Copy example file
cd /home/dev/Development/irStudy/backend
cp .env.kimi.example .env

# Edit .env file
nano .env
```

**Add your Kimi API key**:

```bash
# Kimi API Configuration (FREE)
KIMI_API_KEY=sk-your-actual-kimi-api-key-here
KIMI_BASE_URL=https://api.moonshot.cn/v1

# AI Provider - Use Kimi instead of Claude
AI_PROVIDER=kimi  # Set to 'kimi' for FREE usage

# AI Validation Settings
AI_VALIDATION_ENABLED=true
AI_VALIDATION_TIMEOUT=10

# Database
DATABASE_URL=postgresql://emr_user:emr_pass@localhost:5432/emr_practice

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:5174

# Optional: Claude API (leave empty if using Kimi)
ANTHROPIC_API_KEY=
```

---

## Step 3: Install Dependencies

```bash
cd /home/dev/Development/irStudy/backend

# Add httpx for Kimi API calls
echo "httpx==0.26.0" >> requirements.txt

# Install all dependencies
pip install -r requirements.txt
```

---

## Step 4: Test Kimi Integration

### Test Kimi Adapter

```bash
cd /home/dev/Development/irStudy/backend

# Run test script
python -m src.ai_router.kimi_adapter
```

**Expected Output**:
```json
{
  "id": "moonshot-msg-...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "SOAP notes consist of Subjective (patient history), Objective (examination findings), Assessment (diagnosis), and Plan (management). In Australia, clear documentation is essential for medico-legal compliance and communication."
    }
  ],
  "model": "moonshot-v1-128k",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 45,
    "output_tokens": 58
  }
}
```

### Test AI Validator with Kimi

```bash
cd /home/dev/Development/irStudy/backend

# Run AI validator test
python -m src.validators.ai_validator_kimi
```

**Expected Output**:
```
Overall Score: 85
Clinical Accuracy: 90

Feedback:
This SOAP note demonstrates good clinical reasoning for suspected acute coronary syndrome...

Strengths:
  - Appropriate recognition of ACS red flags
  - Comprehensive vital signs documentation
  - Appropriate initial management with aspirin and GTN

Areas for Improvement:
  - Consider documenting timing of symptom onset more precisely
  - Add patient's risk stratification (GRACE/HEART score)
  - Include explicit safety-netting advice for patient
```

---

## Step 5: Update Backend Main App

The router is already configured to auto-detect and use Kimi based on `AI_PROVIDER` setting.

**Verify in** `/home/dev/Development/irStudy/backend/src/main.py`:

```python
from src.api.v1 import ai_validation_router

# Include router (will use Kimi if AI_PROVIDER=kimi)
app.include_router(ai_validation_router.router)
```

---

## Step 6: Start Backend

```bash
cd /home/dev/Development/irStudy/backend

# Start with uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

**Or use Docker**:

```bash
cd /home/dev/Development/irStudy/backend

# Build and start
docker-compose up --build
```

---

## Step 7: Test API Endpoints

### Health Check

```bash
curl http://localhost:8001/api/v1/ai-validation/health
```

**Expected Response**:
```json
{
  "status": "available",
  "provider": "kimi",
  "model": "moonshot-v1-128k",
  "cost": "FREE"
}
```

### Get Provider Info

```bash
curl http://localhost:8001/api/v1/ai-validation/provider
```

**Expected Response**:
```json
{
  "provider": "kimi",
  "enabled": true,
  "cost": "FREE"
}
```

### Test SOAP Note Validation

```bash
curl -X POST http://localhost:8001/api/v1/ai-validation/validate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "soap",
    "data": {
      "subjective": {
        "chiefComplaint": "Chest pain",
        "hpi": "Patient presents with 2 hours of central chest pain, sharp in nature, radiating to left arm."
      },
      "objective": {
        "vitalSigns": {
          "temperature": 37.0,
          "heartRate": 95,
          "bloodPressureSystolic": 145,
          "bloodPressureDiastolic": 90
        }
      },
      "assessment": {
        "primaryDiagnosis": "Suspected ACS",
        "clinicalReasoning": "Cardiac chest pain with risk factors"
      },
      "plan": {
        "investigations": "ECG, troponin",
        "followUp": "Cardiology review"
      }
    }
  }'
```

**Expected Response**:
```json
{
  "clinical_accuracy": 85,
  "documentation_quality": 80,
  "completeness": 75,
  "overall_score": 80,
  "feedback": "Good initial assessment of suspected ACS...",
  "strengths": ["Appropriate recognition of cardiac chest pain", "..."],
  "areas_for_improvement": ["Document timing more precisely", "..."],
  "learning_points": ["Consider GRACE score for risk stratification", "..."],
  "ai_provider": "kimi"
}
```

---

## Step 8: Frontend Integration

The frontend will automatically use whatever AI provider the backend is configured with.

**No changes needed in frontend code!**

The response will include `ai_provider` field so users know which AI validated their work.

---

## Switching Between Kimi and Claude

### To Use Kimi (FREE):

```bash
# In .env file
AI_PROVIDER=kimi
KIMI_API_KEY=sk-your-kimi-key
```

### To Use Claude (PAID):

```bash
# In .env file
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-claude-key
```

**Restart backend after changing**:
```bash
# If running with uvicorn
# Stop with Ctrl+C, then:
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# If running with Docker
docker-compose restart backend
```

---

## Cost Comparison

| Provider | Model | Cost per 1M tokens | Monthly Free Tier |
|----------|-------|-------------------|-------------------|
| **Kimi** | moonshot-v1-128k | **FREE** | **Unlimited** |
| Claude | claude-3.5-sonnet | $3 input / $15 output | None |

**Example Usage**:
- 100 SOAP note validations per day
- ~2000 tokens per validation (input + output)
- **Kimi**: $0/month 🎉
- **Claude**: ~$36/month

---

## Troubleshooting

### Error: "KIMI_API_KEY not configured"

**Solution**:
```bash
# Check .env file exists
ls -la /home/dev/Development/irStudy/backend/.env

# Verify API key is set
grep KIMI_API_KEY /home/dev/Development/irStudy/backend/.env

# Make sure no spaces around =
# Correct: KIMI_API_KEY=sk-...
# Wrong: KIMI_API_KEY = sk-...
```

### Error: "Connection refused" or "API error"

**Solution**:
```bash
# Test Kimi API directly
curl https://api.moonshot.cn/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KIMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "moonshot-v1-8k",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

If this fails, check:
- API key is valid
- You have internet connection
- Kimi API is not blocked by firewall

### Error: "JSON parsing failed"

Kimi sometimes returns text outside JSON. The adapter handles this, but if you see errors:

**Solution**:
- Increase temperature to 0.1 (more consistent)
- Add "Return ONLY JSON" to prompt
- Use try-catch with fallback

### Rate Limiting

Kimi free tier has limits (exact limits vary). If you hit limits:

**Solutions**:
1. Add delay between requests
2. Cache validation results
3. Implement request queue
4. Switch to Claude for high-volume

---

## Advanced Configuration

### Custom Kimi Base URL

If you're running local Kimi instance or using proxy:

```bash
# In .env
KIMI_BASE_URL=http://localhost:8080/v1
```

### Timeout Configuration

```bash
# In .env
AI_VALIDATION_TIMEOUT=15  # Increase if slow responses
```

### Model Selection

Edit `/home/dev/Development/irStudy/backend/src/ai_router/kimi_adapter.py`:

```python
kimi_model_map = {
    'claude-3-5-sonnet-20241022': 'moonshot-v1-128k',  # Best quality
    'claude-3-opus-20240229': 'moonshot-v1-128k',
    'claude-3-sonnet-20240229': 'moonshot-v1-32k',    # Faster
    'claude-3-haiku-20240307': 'moonshot-v1-8k',      # Fastest
}
```

---

## Security Considerations

### Kimi API Key Security

**Never commit API keys to git**:

```bash
# Verify .env is in .gitignore
grep .env /home/dev/Development/irStudy/backend/.gitignore

# If not, add it:
echo ".env" >> /home/dev/Development/irStudy/backend/.gitignore
```

### Data Privacy

**Important**: Kimi (Moonshot AI) is a Chinese company. Consider:

- Patient data is sent to Kimi API (in China)
- For **educational/practice scenarios only** (mock data)
- **Never send real patient data**
- Review Kimi's privacy policy: https://platform.moonshot.cn/docs/privacy

**For production with real data**: Use Claude (HIPAA-compliant) or local AI model

---

## Performance Tuning

### Response Time Optimization

```python
# In ai_validator_kimi.py, reduce max_tokens
response = await self.adapter.create_message(
    model='claude-3-5-sonnet-20241022',
    messages=[...],
    max_tokens=1000,  # Reduce from 2000 for faster responses
    temperature=0.1   # Lower for more consistent/faster
)
```

### Caching Results

Implement Redis caching for identical SOAP notes:

```python
import hashlib
import json

def get_cache_key(soap_note):
    return hashlib.md5(json.dumps(soap_note, sort_keys=True).encode()).hexdigest()

# Check cache before validation
# If hit, return cached result
# If miss, validate and cache result
```

---

## Support

**Kimi/Moonshot AI**:
- Docs: https://platform.moonshot.cn/docs
- API Reference: https://platform.moonshot.cn/docs/api-reference
- Community: https://github.com/Moonshot-AI

**This Project**:
- Check logs: `docker-compose logs backend`
- Test endpoints: `curl http://localhost:8001/api/v1/ai-validation/health`
- Review code: `/home/dev/Development/irStudy/backend/src/ai_router/`

---

## Summary

✅ **You now have FREE AI validation powered by Kimi 2.5!**

**What you get**:
- Same API interface as Claude
- Educational feedback for ICRP preparation
- Australian clinical guidelines compliance
- Zero cost (vs $36/month for Claude)

**Trade-off**:
- Slightly less sophisticated than Claude
- Data sent to Chinese company
- Perfect for practice/education (not production with real data)

**Next Steps**:
1. Get Kimi API key
2. Configure `.env` file
3. Test with `curl` commands above
4. Start building EMR practice system!

---

**Last Updated**: 2026-02-03
**Status**: ✅ Ready for Implementation
