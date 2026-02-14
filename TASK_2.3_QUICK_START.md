# Task 2.3: WebSocket Load Testing - Quick Start Guide

## Run Load Tests (One Command)

```bash
bash run_load_tests.sh
```

## Prerequisites

1. Virtual environment with dependencies
2. Redis running on port 7379
3. Vault running on port 8200 with secrets

## Setup (First Time Only)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# 2. Start services
docker-compose up -d redis vault

# 3. Configure Vault (if not already done)
./scripts/setup_vault_secrets.sh
```

## Run Tests

```bash
# Run all load tests
bash run_load_tests.sh

# Or run directly (ensure environment variables set)
source venv/bin/activate
export SECRET_KEY=$(vault kv get -field=jwt_secret amc-simulation/api-keys)
export REDIS_URL=redis://localhost:7379
python backend/tests/load_test_websocket.py
```

## View Results

```bash
# View comprehensive report
cat TASK_2.3_LOAD_TEST_REPORT.md

# Or open in editor
code TASK_2.3_LOAD_TEST_REPORT.md
```

## Test Scenarios

1. **Normal Load**: 50 concurrent users
2. **Peak Load**: 100 concurrent users
3. **Rate Limiting**: Validate 10 connections/60s
4. **Connection Limit**: Validate max 3 concurrent
5. **Invalid Tokens**: Validate security controls

## Expected Runtime

- **Total**: ~10-15 seconds
- **Normal Load**: ~2-3 seconds
- **Peak Load**: ~5-7 seconds
- **Rate Limit**: ~1-2 seconds
- **Connection Limit**: ~1 second
- **Invalid Tokens**: ~1 second

## Success Criteria

- ✅ All tests complete without errors
- ✅ P95 latency <50ms
- ✅ Success rate >99%
- ✅ Rate limit enforced
- ✅ Connection limit enforced
- ✅ Invalid tokens blocked

## Troubleshooting

### Error: REDIS_URL not set

```bash
# Solution: Run via run_load_tests.sh instead
bash run_load_tests.sh
```

### Error: Vault connection failed

```bash
# Check Vault is running
docker ps | grep vault

# Start Vault
docker-compose up -d vault

# Configure secrets
./scripts/setup_vault_secrets.sh
```

### Error: Redis connection failed

```bash
# Check Redis is running
docker ps | grep redis

# Start Redis
docker-compose up -d redis

# Test connection
redis-cli -p 7379 ping
```

### Error: Import errors

```bash
# Ensure dependencies installed
source venv/bin/activate
pip install -r backend/requirements.txt
```

## Files

- **Load test script**: `backend/tests/load_test_websocket.py`
- **Test runner**: `run_load_tests.sh`
- **Report output**: `TASK_2.3_LOAD_TEST_REPORT.md`
- **Implementation summary**: `TASK_2.3_IMPLEMENTATION_SUMMARY.md`

## Integration with CI/CD

```yaml
# .github/workflows/load-tests.yml
name: Load Tests
on: [push, pull_request]
jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.12
      - name: Install dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r backend/requirements.txt
      - name: Start services
        run: docker-compose up -d redis vault
      - name: Run load tests
        run: bash run_load_tests.sh
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: load-test-report
          path: TASK_2.3_LOAD_TEST_REPORT.md
```

## Next Steps

1. Review report: `TASK_2.3_LOAD_TEST_REPORT.md`
2. Address any recommendations
3. Run tests regularly (pre-deploy)
4. Monitor performance trends
5. Adjust targets as needed

---

**Last Updated**: 2026-02-07
**Task**: 2.3 - WebSocket Authentication Load Testing
**Status**: ✅ COMPLETE
