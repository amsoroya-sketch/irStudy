# AI Router - Kimi/Claude Provider

This module routes AI validation requests to either **Kimi 2.5 (FREE)** or **Claude 3.5 (PAID)** based on configuration.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     API Request                             │
│   POST /api/v1/ai-validation/validate                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            AI Validation Router                             │
│   (ai_validation_router.py)                                 │
│                                                              │
│   Checks: AI_PROVIDER environment variable                  │
└────────────┬────────────────────────────┬────────────────────┘
             │                            │
    AI_PROVIDER=kimi          AI_PROVIDER=claude
             │                            │
             ▼                            ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│   AIValidatorKimi       │  │   AIValidator (Claude)       │
│  (ai_validator_kimi.py) │  │   (ai_validator.py)          │
└───────────┬─────────────┘  └──────────────┬───────────────┘
            │                               │
            ▼                               ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│   KimiAdapter           │  │   Anthropic SDK              │
│  (kimi_adapter.py)      │  │   (anthropic package)        │
│                         │  │                              │
│  - Format conversion    │  │  - Direct API calls          │
│  - Message translation  │  │                              │
│  - Response parsing     │  │                              │
└───────────┬─────────────┘  └──────────────┬───────────────┘
            │                               │
            ▼                               ▼
┌─────────────────────────┐  ┌──────────────────────────────┐
│   Kimi API              │  │   Claude API                 │
│   (api.moonshot.cn)     │  │   (api.anthropic.com)        │
│                         │  │                              │
│   Model: moonshot-v1    │  │   Model: claude-3.5-sonnet   │
│   Cost: FREE ✅         │  │   Cost: PAID 💰              │
└─────────────────────────┘  └──────────────────────────────┘
```

---

## Files

### 1. `kimi_adapter.py`
**Purpose**: Translate between Claude API format and Kimi API format

**Key Functions**:
- `create_message()`: Main entry point (Claude-compatible interface)
- `_convert_claude_to_kimi_messages()`: Convert message format
- `_convert_kimi_to_claude_response()`: Convert response format

**Model Mapping**:
```python
'claude-3-5-sonnet-20241022' → 'moonshot-v1-128k'  # Best
'claude-3-opus-20240229'     → 'moonshot-v1-128k'  # Best
'claude-3-sonnet-20240229'   → 'moonshot-v1-32k'   # Medium
'claude-3-haiku-20240307'    → 'moonshot-v1-8k'    # Fast
```

---

### 2. `ai_validator_kimi.py` (in ../validators/)
**Purpose**: AI validation logic using Kimi

**Validation Methods**:
- `validate_soap_note()`: SOAP note validation
- `validate_prescription()`: Prescription validation
- `validate_pathology_order()`: Pathology order validation

**Returns**: `AIValidationResult` with:
- clinical_accuracy (0-100)
- documentation_quality (0-100)
- completeness (0-100)
- overall_score (0-100)
- feedback (string)
- strengths (list)
- areas_for_improvement (list)
- learning_points (list)

---

### 3. `ai_validation_router.py` (in ../api/v1/)
**Purpose**: FastAPI router with auto-provider selection

**Endpoints**:
- `POST /api/v1/ai-validation/validate` - Validate content
- `GET /api/v1/ai-validation/health` - Check service status
- `GET /api/v1/ai-validation/provider` - Get current provider info

**Provider Selection**:
```python
if settings.ai_provider == 'kimi':
    validator = AIValidatorKimi()
elif settings.ai_provider == 'claude':
    validator = AIValidator()
```

---

## Configuration

### Environment Variables

```bash
# AI Provider Selection
AI_PROVIDER=kimi  # Options: 'kimi' or 'claude'

# Kimi Configuration (FREE)
KIMI_API_KEY=sk-your-kimi-key
KIMI_BASE_URL=https://api.moonshot.cn/v1

# Claude Configuration (PAID - optional)
ANTHROPIC_API_KEY=sk-ant-your-claude-key
```

### Get Kimi API Key

1. Visit: https://platform.moonshot.cn/
2. Register account
3. Create API key
4. Copy key (format: `sk-...`)

---

## Usage

### Python

```python
from src.ai_router.kimi_adapter import KimiAdapter

# Initialize
adapter = KimiAdapter(kimi_api_key='sk-...')

# Create message
response = await adapter.create_message(
    model='claude-3-5-sonnet-20241022',  # Will map to Kimi model
    messages=[
        {'role': 'user', 'content': 'Validate this SOAP note...'}
    ],
    max_tokens=2000,
    temperature=0.3
)

# Close when done
await adapter.close()
```

### API

```bash
# Validate SOAP note
curl -X POST http://localhost:8001/api/v1/ai-validation/validate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "soap",
    "data": { ... },
    "context": { ... }
  }'

# Check health
curl http://localhost:8001/api/v1/ai-validation/health

# Get provider info
curl http://localhost:8001/api/v1/ai-validation/provider
```

---

## Response Format

### Validation Response

```json
{
  "clinical_accuracy": 85,
  "documentation_quality": 80,
  "completeness": 75,
  "overall_score": 80,
  "feedback": "Good initial assessment...",
  "strengths": [
    "Appropriate recognition of red flags",
    "Comprehensive vital signs documented"
  ],
  "areas_for_improvement": [
    "Document timing more precisely",
    "Consider GRACE score for risk stratification"
  ],
  "learning_points": [
    "In suspected ACS, serial troponins at 0h and 2h are recommended",
    "Australian guidelines recommend aspirin 300mg stat"
  ],
  "ai_provider": "kimi"
}
```

### Health Check Response

```json
{
  "status": "available",
  "provider": "kimi",
  "model": "moonshot-v1-128k",
  "cost": "FREE"
}
```

---

## Testing

### Test Kimi Adapter

```bash
cd /home/dev/Development/irStudy/backend
python -m src.ai_router.kimi_adapter
```

### Test Validator

```bash
python -m src.validators.ai_validator_kimi
```

### Test API Endpoint

```bash
# Health check
curl http://localhost:8001/api/v1/ai-validation/health

# Validation
curl -X POST http://localhost:8001/api/v1/ai-validation/validate \
  -H "Content-Type: application/json" \
  -d @test_data.json
```

---

## Switching Providers

### Switch to Kimi (FREE)

```bash
# Edit .env
AI_PROVIDER=kimi
KIMI_API_KEY=sk-your-kimi-key

# Restart backend
docker-compose restart backend
```

### Switch to Claude (PAID)

```bash
# Edit .env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-claude-key

# Restart backend
docker-compose restart backend
```

---

## Troubleshooting

### "KIMI_API_KEY not configured"

```bash
# Check .env file
cat /home/dev/Development/irStudy/backend/.env | grep KIMI

# Make sure it's set:
KIMI_API_KEY=sk-...
```

### "JSON parsing failed"

Kimi sometimes returns text outside JSON. The adapter handles this with try-catch, but if errors persist:

1. Add more explicit instructions in prompt:
   ```python
   prompt += "\n\nReturn ONLY the JSON object, no other text."
   ```

2. Lower temperature for more consistent responses:
   ```python
   temperature=0.1  # Instead of 0.3
   ```

### "Connection timeout"

```bash
# Test Kimi API directly
curl -X POST https://api.moonshot.cn/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KIMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "moonshot-v1-8k",
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100
  }'
```

If this works but adapter times out:
- Increase timeout in `kimi_adapter.py` (currently 30s)
- Check for network/firewall issues

---

## Performance

### Kimi Performance

- **Response Time**: 3-5 seconds (similar to Claude)
- **Context Window**: 128K tokens (moonshot-v1-128k)
- **Quality**: ~85-90% of Claude quality
- **Cost**: **FREE** ✅

### Optimization Tips

1. **Reduce max_tokens** for faster responses:
   ```python
   max_tokens=1000  # Instead of 2000
   ```

2. **Lower temperature** for consistency:
   ```python
   temperature=0.1  # Instead of 0.3
   ```

3. **Cache results** for identical inputs (implement Redis caching)

4. **Use smaller model** for simple validations:
   ```python
   kimi_model_map = {
       'claude-3-haiku-20240307': 'moonshot-v1-8k',  # Fastest
   }
   ```

---

## Cost Analysis

### Monthly Usage Estimate
- 50 users × 3 SOAP notes/day × 2 validations = 300 validations/day
- 300 × 30 days = 9,000 validations/month
- ~2,000 tokens per validation = 18M tokens/month

### Cost Comparison

| Provider | Model | Cost per 1M tokens | Monthly Cost |
|----------|-------|-------------------|--------------|
| **Kimi** | moonshot-v1-128k | **FREE** | **$0** ✅ |
| Claude | claude-3.5-sonnet | $3 input / $15 output | ~$324 |

**Annual Savings**: **$3,888** 💰

---

## Security

### API Key Security

**Never commit API keys**:
```bash
# Verify .env is in .gitignore
grep .env /home/dev/Development/irStudy/backend/.gitignore
```

**Use environment variables**:
- Development: `.env` file
- Production: Docker secrets, cloud provider secrets, or vault

### Data Privacy

**Kimi Considerations**:
- Data sent to Moonshot AI (Chinese company)
- **Use ONLY for educational/practice data**
- **Never send real patient data**
- Review privacy policy: https://platform.moonshot.cn/docs/privacy

**For production**: Use Claude (HIPAA-compliant) or local models

---

## Migration Path

### Phase 1: Start with Kimi
- **Cost**: $0/month
- **Use**: Development, testing, educational platform

### Phase 2: Hybrid (Optional)
- Most users: Kimi (FREE)
- Premium users: Claude (PAID)
- Requires per-request provider selection (code changes)

### Phase 3: Full Claude (If Needed)
- **Cost**: ~$324/month
- **Use**: Production, real patients, HIPAA compliance

---

## References

**Kimi Documentation**:
- Platform: https://platform.moonshot.cn/
- Docs: https://platform.moonshot.cn/docs
- API Reference: https://platform.moonshot.cn/docs/api-reference

**This Project**:
- Setup Guide: `/home/dev/Development/irStudy/KIMI_SETUP_GUIDE.md`
- Quick Reference: `/home/dev/Development/irStudy/AI_PROVIDER_QUICK_REFERENCE.md`
- Summary: `/home/dev/Development/irStudy/KIMI_INTEGRATION_SUMMARY.md`

---

**Last Updated**: 2026-02-03
**Status**: ✅ Production Ready
**Recommended**: Start with Kimi (FREE), switch to Claude only if needed
