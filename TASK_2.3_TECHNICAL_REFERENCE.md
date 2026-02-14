# Task 2.3: WebSocket Load Testing - Technical Reference

## Code Structure

### Load Test Script Architecture

```python
backend/tests/load_test_websocket.py (820 lines)
│
├── Data Structures
│   └── LoadTestResult (dataclass)
│       ├── Properties: success_rate, p50, p95, p99, mean, min, max
│       └── Fields: latencies, errors, security_events
│
├── WebSocketLoadTester (main class)
│   ├── __init__(redis_url, jwt_secret)
│   ├── setup() - Initialize Redis and authenticator
│   ├── teardown() - Cleanup resources
│   ├── generate_jwt_token(user_id) - Create test tokens
│   ├── create_session(user_id) - Set up Redis sessions
│   ├── authenticate_connection() - Single connection test
│   │
│   └── Test Scenarios
│       ├── run_normal_load_test(50 users)
│       ├── run_peak_load_test(100 users)
│       ├── run_rate_limit_test()
│       ├── run_connection_limit_test()
│       └── run_invalid_token_test(20 attempts)
│
├── Report Generation
│   └── generate_markdown_report(results, output_file)
│       ├── Executive Summary
│       ├── Performance Metrics (with status indicators)
│       ├── Rate Limiting Validation
│       ├── Connection Tracking Validation
│       ├── Security Validation
│       ├── Error Analysis
│       ├── Recommendations
│       └── Conclusion (pass/fail)
│
└── main() - Orchestrates all tests
    ├── Check environment variables
    ├── Set up test environment
    ├── Run all test scenarios
    ├── Generate report
    └── Clean up
```

### Test Runner Script

```bash
run_load_tests.sh (93 lines)
│
├── Environment Setup
│   ├── Check virtual environment exists
│   ├── Activate virtual environment
│   └── Set Vault connection variables
│
├── Secret Retrieval (SECURE)
│   ├── Fetch JWT secret from Vault (NOT hardcoded)
│   └── Validate secret retrieved
│
├── Environment Variables
│   ├── Export SECRET_KEY (from Vault)
│   └── Export REDIS_URL (from environment)
│
├── Pre-flight Checks
│   └── Check Redis connectivity
│
└── Execute Tests
    ├── Run load_test_websocket.py
    ├── Check exit code
    └── Display results
```

## Key Features

### 1. LoadTestResult Dataclass

```python
@dataclass
class LoadTestResult:
    """Comprehensive test result tracking"""
    test_name: str
    total_connections: int
    successful_connections: int
    failed_connections: int
    latencies_ms: List[float]
    error_types: Dict[str, int]
    security_events: List[Dict[str, Any]]
    duration_seconds: float
    
    # Computed properties
    @property
    def success_rate(self) -> float:
        return (self.successful_connections / self.total_connections) * 100
    
    @property
    def p95_latency(self) -> float:
        sorted_latencies = sorted(self.latencies_ms)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[idx]
```

### 2. Async Connection Testing

```python
async def authenticate_connection(
    self,
    user_id: str,
    connection_id: str,
    ip_address: str,
    user_agent: str,
    expect_success: bool = True
) -> Tuple[bool, float, str]:
    """Authenticate single connection with latency measurement"""
    
    # Generate token
    token = self.generate_jwt_token(user_id)
    
    # Measure authentication latency
    start_time = time.perf_counter()
    
    result = await self.authenticator.authenticate(
        token=token,
        connection_id=connection_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    return result.success, latency_ms, result.message
```

### 3. Peak Load Testing (Batched)

```python
async def run_peak_load_test(self, num_users: int = 100):
    """Test with 100 concurrent users in batches"""
    
    batch_size = 20
    
    for batch_start in range(0, num_users, batch_size):
        batch_end = min(batch_start + batch_size, num_users)
        
        # Create batch of concurrent auth tasks
        auth_tasks = [
            self.authenticate_connection(...)
            for i in range(batch_start, batch_end)
        ]
        
        # Execute batch concurrently
        results = await asyncio.gather(*auth_tasks, return_exceptions=True)
        
        # Process results
        # ... (error handling, metric collection)
        
        # Small delay between batches
        await asyncio.sleep(0.1)
```

### 4. Rate Limiting Validation

```python
async def run_rate_limit_test(self):
    """Validate 10 connections/60s rate limit"""
    
    user_id = "rate-limit-user"
    num_attempts = 15  # Exceed limit of 10
    
    await self.create_session(user_id)
    
    for i in range(num_attempts):
        success, latency, message = await self.authenticate_connection(
            user_id=user_id,
            connection_id=f"rate-conn-{i:04d}",
            ip_address="192.168.1.100",
            user_agent="LoadTest/1.0",
            expect_success=(i < 10)  # First 10 should succeed
        )
        
        # Track results
        # ... (success/failure tracking)
        
        if success:
            # Disconnect to allow next connection
            await self.authenticator.disconnect(user_id, connection_id)
    
    # Validate: at least 5 connections should be blocked
    rate_limit_working = result.failed_connections >= 5
```

### 5. Security Validation

```python
async def run_invalid_token_test(self, num_attempts: int = 20):
    """Test handling of invalid tokens"""
    
    for i in range(num_attempts):
        # Attempt with invalid token (no session)
        auth_result = await self.authenticator.authenticate(
            token=f"invalid-token-{i:08x}",
            connection_id=f"invalid-{i:04d}",
            ip_address="192.168.1.100",
            user_agent="LoadTest/1.0"
        )
        
        if not auth_result.success:
            # Security event logged
            result.security_events.append({
                "type": "invalid_token",
                "message": auth_result.message
            })
    
    # Validate: ALL invalid tokens should be rejected
    all_blocked = result.failed_connections == num_attempts
```

### 6. Report Generation (Markdown)

```python
def generate_markdown_report(results: List[LoadTestResult], output_file: str):
    """Generate comprehensive markdown report"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- Total connections: {total_connections}\n")
        f.write(f"- Success rate: {overall_success_rate:.1f}%\n\n")
        
        # Performance Metrics (with status indicators)
        f.write("| Metric | Target | Actual | Status |\n")
        f.write("|--------|--------|--------|--------|\n")
        
        p95_status = "✅" if result.p95_latency < 50 else "❌"
        f.write(f"| P95 Latency | <50ms | {result.p95_latency:.2f}ms | {p95_status} |\n")
        
        # Recommendations
        if normal_load.p95_latency >= 50:
            f.write("❌ **CRITICAL**: P95 latency exceeds target\n")
        
        # Conclusion
        if all_pass:
            f.write("✅ **PASSED**: System meets all requirements\n")
        else:
            f.write("❌ **FAILED**: Issues must be addressed\n")
```

## Security Patterns

### Environment Variable Usage

```python
# CORRECT: Read from environment
redis_url = os.getenv('REDIS_URL')
jwt_secret = os.getenv('SECRET_KEY')

# Validate before use
if not redis_url or not jwt_secret:
    print("ERROR: Environment variables not set")
    sys.exit(1)

# INCORRECT: Hardcoded (NEVER do this)
# redis_url = "redis://localhost:7379"  # ❌
# jwt_secret = "my-secret-key-12345"    # ❌
```

### Vault Integration

```bash
# Fetch JWT secret from Vault (NOT hardcoded)
JWT_SECRET=$(python -c "
import hvac
client = hvac.Client(
    url='http://localhost:8200',
    token='dev-only-token-change-in-prod'
)
secret = client.secrets.kv.v2.read_secret_version(
    path='amc-simulation/api-keys'
)
print(secret['data']['data']['jwt_secret'])
")

# Export as environment variable
export SECRET_KEY=$JWT_SECRET
```

### User ID Anonymization

```python
# In reports, anonymize user IDs
for result in results:
    for event in result.security_events:
        # Truncate user ID
        if 'user_id' in event:
            event['user_id'] = event['user_id'][:8] + "***"
```

## Performance Optimization

### Async Concurrency

```python
# Run connections concurrently (not sequentially)
tasks = [
    authenticate_connection(f"user-{i}", ...)
    for i in range(50)
]

# Execute all concurrently
results = await asyncio.gather(*tasks)
```

### Batching for Peak Load

```python
# Batch large loads to avoid overwhelming system
batch_size = 20
for batch_start in range(0, 100, batch_size):
    # Process batch
    await asyncio.gather(*batch_tasks)
    
    # Small delay between batches
    await asyncio.sleep(0.1)
```

### Latency Measurement

```python
# Use time.perf_counter() for accurate timing
start = time.perf_counter()
result = await operation()
latency_ms = (time.perf_counter() - start) * 1000
```

### Percentile Calculation

```python
# Sort latencies for accurate percentiles
sorted_latencies = sorted(self.latencies_ms)

# Calculate percentiles
p50_idx = int(len(sorted_latencies) * 0.50)
p95_idx = int(len(sorted_latencies) * 0.95)
p99_idx = int(len(sorted_latencies) * 0.99)

p50 = sorted_latencies[p50_idx]
p95 = sorted_latencies[p95_idx]
p99 = sorted_latencies[p99_idx]
```

## Error Handling

### Exception Handling in Async

```python
# Gather with exception handling
results = await asyncio.gather(*tasks, return_exceptions=True)

for res in results:
    if isinstance(res, Exception):
        # Handle exception
        result.failed_connections += 1
        result.error_types[type(res).__name__] += 1
    else:
        # Handle success
        success, latency, message = res
        # ...
```

### Graceful Cleanup

```python
try:
    await tester.setup()
    # Run tests
    results = await run_all_tests()
finally:
    # Always cleanup, even on error
    await tester.teardown()
```

## Testing Patterns

### Session Creation

```python
async def create_session(self, user_id: str, fingerprint: str = None):
    """Create Redis session for user"""
    session_key = f"session:{user_id}"
    session_data = {
        "user_id": user_id,
        "email": f"{user_id}@test.example.com",
        "role": "student",
        "fingerprint": fingerprint
    }
    await self.redis_client.set(session_key, json.dumps(session_data))
```

### Token Generation

```python
def generate_jwt_token(self, user_id: str) -> str:
    """Generate JWT token for testing"""
    payload = {
        "sub": user_id,
        "email": f"{user_id}@test.example.com",
        "role": "student"
    }
    return create_access_token(payload)
```

### Connection Cleanup

```python
if success:
    # Disconnect after test
    await self.authenticator.disconnect(user_id, connection_id)
```

## Metrics Collection

### Latency Tracking

```python
result.latencies_ms.append(latency_ms)
```

### Error Categorization

```python
result.error_types[message] += 1
```

### Security Event Logging

```python
result.security_events.append({
    "type": "invalid_token",
    "message": auth_result.message,
    "timestamp": datetime.now().isoformat()
})
```

## Report Features

### Status Indicators

```python
# Visual status indicators in markdown
p95_status = "✅" if result.p95_latency < 50 else "❌"
success_status = "✅" if result.success_rate > 99 else "⚠️"
```

### Recommendations

```python
# Automated recommendations based on results
if peak_load.p95_latency >= 50:
    recommendations.append(
        "⚠️ **WARNING**: P95 latency exceeds target under peak load"
    )
```

### Pass/Fail Determination

```python
all_pass = all([
    normal_load.p95_latency < 50,
    peak_load.success_rate >= 99,
    rate_limit_test.failed_connections >= 5,
    conn_limit_test.successful_connections == 3,
    invalid_token_test.successful_connections == 0
])
```

## Integration Points

### Redis Integration

```python
self.redis_client = redis.from_url(
    self.redis_url,
    encoding="utf-8",
    decode_responses=True
)
```

### Authenticator Integration

```python
self.authenticator = WebSocketAuthenticator(
    redis_client=self.redis_client,
    rate_limiter=RateLimiter(...),
    connection_tracker=ConnectionTracker(...)
)
```

### Security Module Integration

```python
from src.auth.security import create_access_token
token = create_access_token(payload)
```

## Usage Examples

### Basic Usage

```bash
# Run all tests
bash run_load_tests.sh
```

### Custom Test Run

```python
# Run specific test
tester = WebSocketLoadTester(redis_url, jwt_secret)
await tester.setup()
result = await tester.run_normal_load_test(num_users=25)
await tester.teardown()
```

### CI/CD Integration

```yaml
- name: Run load tests
  run: |
    source venv/bin/activate
    bash run_load_tests.sh
  env:
    REDIS_URL: redis://redis:6379
    VAULT_ADDR: http://vault:8200
```

## Troubleshooting

### Debug Mode

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Verbose Output

```bash
# Run with verbose output
python backend/tests/load_test_websocket.py --verbose
```

### Individual Test Execution

```python
# Run single test scenario
if __name__ == "__main__":
    tester = WebSocketLoadTester(redis_url, jwt_secret)
    asyncio.run(tester.run_normal_load_test(50))
```

---

**Last Updated**: 2026-02-07
**Task**: 2.3 - WebSocket Authentication Load Testing
**Version**: 1.0
