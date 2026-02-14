# Week 2 API Documentation - WebSocket Authentication

**Version**: 1.0  
**Last Updated**: 2026-02-07  
**Project**: AMC Clinical Exam Simulation v2.0  
**Sprint**: Week 2 - Enhanced WebSocket Authentication

---

## Overview

Week 2 implements a zero-trust WebSocket authentication system with 6-step validation. This document provides comprehensive API reference for developers integrating with the WebSocket authentication system.

### Architecture

```
Client Application
    ↓ (HTTPS)
POST /api/v1/auth/login
    ↓ (Response: JWT token + session ID)
Client receives JWT token
    ↓ (WebSocket with headers)
WS /ws (with Authorization header)
    ↓ (6-step authentication)
WebSocket connection established
```

### Key Features

- **JWT-based authentication**: Secure token validation
- **Session correlation**: Redis-backed session verification
- **Token fingerprinting**: Device/browser validation
- **Rate limiting**: 10 connections/60 seconds per user
- **Connection tracking**: Max 3 concurrent connections
- **Security event logging**: All attempts logged for audit

---

## Authentication Endpoint

### WebSocket Connection URL

```
ws://localhost:8000/ws
wss://api.example.com/ws  (production - TLS required)
```

### Required Headers

```http
Authorization: Bearer <JWT_TOKEN>
X-Session-ID: <SESSION_UUID>
X-Fingerprint: <SHA256_HASH>
```

**Header Descriptions**:

| Header | Required | Format | Description |
|--------|----------|--------|-------------|
| `Authorization` | Yes | `Bearer <token>` | JWT access token from `/api/v1/auth/login` |
| `X-Session-ID` | Yes | UUID v4 | Session identifier from Redis |
| `X-Fingerprint` | Yes | SHA-256 hex (64 chars) | Device fingerprint hash |

### Fingerprint Generation

**Client-Side** (JavaScript):
```javascript
// Generate device fingerprint
const generateFingerprint = () => {
  const data = [
    window.location.hostname,           // IP address (proxy-safe)
    navigator.userAgent,                // Browser/OS
    screen.width + 'x' + screen.height, // Screen resolution
  ].join('|');
  
  // SHA-256 hash
  return crypto.subtle.digest('SHA-256', 
    new TextEncoder().encode(data)
  ).then(hash => {
    return Array.from(new Uint8Array(hash))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  });
};
```

**Python Client**:
```python
import hashlib

def generate_fingerprint(ip_address: str, user_agent: str, screen_resolution: str) -> str:
    """Generate device fingerprint for WebSocket authentication"""
    data = f"{ip_address}{user_agent}{screen_resolution}"
    return hashlib.sha256(data.encode()).hexdigest()
```

---

## Request Format

### WebSocket Connection Request

**Endpoint**: `WS /ws`

**Headers**:
```http
GET /ws HTTP/1.1
Host: localhost:8000
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==
Sec-WebSocket-Version: 13
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Session-ID: 550e8400-e29b-41d4-a716-446655440000
X-Fingerprint: 5d41402abc4b2a76b9719d911017c592e31e8f8e...
```

**Example**: Python with `websockets` library:
```python
import asyncio
import websockets
import json

async def connect_websocket():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    session_id = "550e8400-e29b-41d4-a716-446655440000"
    fingerprint = "5d41402abc4b2a76b9719d911017c592e31e8f8e..."
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Session-ID": session_id,
        "X-Fingerprint": fingerprint
    }
    
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri, extra_headers=headers) as websocket:
            print("✅ Connected successfully")
            
            # Send ping
            await websocket.send(json.dumps({"type": "ping"}))
            response = await websocket.recv()
            print(f"📩 Received: {response}")
            
            # Keep connection alive with heartbeat
            while True:
                await asyncio.sleep(30)
                await websocket.send(json.dumps({"type": "ping"}))
                
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ Connection failed: {e}")

# Run
asyncio.run(connect_websocket())
```

**Example**: JavaScript (Browser):
```javascript
// 1. Get JWT token from login
const loginResponse = await fetch('/api/v1/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email: 'user@example.com', password: 'password123'})
});
const {access_token, session_id} = await loginResponse.json();

// 2. Generate fingerprint
const fingerprint = await generateFingerprint();

// 3. Connect WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

// Send headers via subprotocol (browser WebSocket API limitation workaround)
// Note: In production, use proper WebSocket library that supports custom headers
ws.onopen = () => {
  console.log('✅ WebSocket connected');
  
  // Heartbeat every 30 seconds
  setInterval(() => {
    ws.send(JSON.stringify({type: 'ping'}));
  }, 30000);
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('📩 Received:', data);
};

ws.onerror = (error) => {
  console.error('❌ WebSocket error:', error);
};

ws.onclose = (event) => {
  console.log('🔌 WebSocket closed:', event.code, event.reason);
};
```

**Example**: Rust:
```rust
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use futures_util::{SinkExt, StreamExt};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
    let session_id = "550e8400-e29b-41d4-a716-446655440000";
    let fingerprint = "5d41402abc4b2a76b9719d911017c592e31e8f8e...";
    
    let url = url::Url::parse("ws://localhost:8000/ws")?;
    
    let request = http::Request::builder()
        .uri(url.as_str())
        .header("Authorization", format!("Bearer {}", token))
        .header("X-Session-ID", session_id)
        .header("X-Fingerprint", fingerprint)
        .body(())?;
    
    let (ws_stream, _) = connect_async(request).await?;
    println!("✅ WebSocket connected");
    
    let (mut write, mut read) = ws_stream.split();
    
    // Send ping
    write.send(Message::Text(r#"{"type":"ping"}"#.into())).await?;
    
    // Read response
    if let Some(msg) = read.next().await {
        println!("📩 Received: {:?}", msg?);
    }
    
    Ok(())
}
```

---

## Response Format

### Success Response

**HTTP Status**: `101 Switching Protocols`

**WebSocket Handshake**:
```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: HSmrc0sMlYUkAGmm5OPpG2HaGWk=
```

**Initial Message** (JSON):
```json
{
  "type": "connection_established",
  "connection_id": "conn-abc123xyz",
  "timestamp": "2026-02-07T10:30:45.123456Z",
  "metadata": {
    "user_id": "user-12345678",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "authenticated_at": "2026-02-07T10:30:45.123456Z"
  }
}
```

### Failure Response

**HTTP Status**: Various (see Error Codes below)

**WebSocket Close Frame**:
```
Close Code: 1008 (Policy Violation)
Close Reason: "Authentication failed: <error message>"
```

**No WebSocket connection established** - client receives HTTP error response instead.

---

## Error Codes

### HTTP Status Codes

| Code | Name | Description | Recovery |
|------|------|-------------|----------|
| 400 | Bad Request | Missing/invalid headers | Check request format |
| 401 | Unauthorized | Invalid/expired JWT token | Get new token via `/api/v1/auth/login` |
| 403 | Forbidden | Session mismatch, fingerprint issue, max connections | See specific error message |
| 429 | Too Many Requests | Rate limit exceeded | Wait `retry_after` seconds |
| 500 | Internal Server Error | Server-side error | Retry later, contact support |
| 503 | Service Unavailable | Redis/Vault unavailable | Retry later |

### Authentication Error Codes

#### 401 Unauthorized

**Error**: Invalid token signature
```json
{
  "error": "unauthorized",
  "message": "Invalid token signature",
  "code": "INVALID_TOKEN_SIGNATURE"
}
```
**Recovery**: Get new token via `/api/v1/auth/login`

---

**Error**: Token expired
```json
{
  "error": "unauthorized",
  "message": "Token has expired",
  "code": "TOKEN_EXPIRED",
  "metadata": {
    "expired_at": "2026-02-07T09:30:45Z",
    "current_time": "2026-02-07T10:30:45Z"
  }
}
```
**Recovery**: Get new token via `/api/v1/auth/login`

---

**Error**: Invalid token type
```json
{
  "error": "unauthorized",
  "message": "Invalid token type (expected: access)",
  "code": "INVALID_TOKEN_TYPE"
}
```
**Recovery**: Ensure using access token, not refresh token

---

#### 403 Forbidden

**Error**: Session not found
```json
{
  "error": "forbidden",
  "message": "Session not found or expired",
  "code": "SESSION_NOT_FOUND",
  "metadata": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```
**Recovery**: Log out and log back in to create new session

---

**Error**: Session user mismatch
```json
{
  "error": "forbidden",
  "message": "Session does not belong to user",
  "code": "SESSION_USER_MISMATCH"
}
```
**Recovery**: Contact support (possible security issue)

---

**Error**: Fingerprint mismatch
```json
{
  "error": "warning",
  "message": "Token fingerprint mismatch detected",
  "code": "FINGERPRINT_MISMATCH",
  "metadata": {
    "expected": "5d41402abc4b2a76b...",
    "received": "a1b2c3d4e5f6g7h8i..."
  }
}
```
**Recovery**: Connection allowed but logged. If persistent, regenerate fingerprint.

---

**Error**: Max connections exceeded
```json
{
  "error": "forbidden",
  "message": "Maximum concurrent connections exceeded",
  "code": "MAX_CONNECTIONS_EXCEEDED",
  "metadata": {
    "current_connections": 3,
    "max_allowed": 3,
    "active_connections": [
      {
        "connection_id": "conn-abc123",
        "connected_at": "2026-02-07T10:00:00Z",
        "last_heartbeat": "2026-02-07T10:29:00Z"
      },
      {
        "connection_id": "conn-def456",
        "connected_at": "2026-02-07T10:15:00Z",
        "last_heartbeat": "2026-02-07T10:30:00Z"
      },
      {
        "connection_id": "conn-ghi789",
        "connected_at": "2026-02-07T10:25:00Z",
        "last_heartbeat": "2026-02-07T10:30:30Z"
      }
    ]
  }
}
```
**Recovery**: Close unused connections, wait for stale connections to timeout (5 minutes)

---

#### 429 Too Many Requests

**Error**: Rate limit exceeded
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many connection attempts",
  "code": "RATE_LIMIT_EXCEEDED",
  "metadata": {
    "limit": 10,
    "window_seconds": 60,
    "current_attempts": 11,
    "retry_after": 45,
    "reset_at": "2026-02-07T10:31:30Z"
  }
}
```
**Recovery**: Wait `retry_after` seconds before retrying

**Response Headers**:
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1706355090
```

---

## Rate Limiting

### Limits

| Resource | Limit | Window | Per |
|----------|-------|--------|-----|
| WebSocket connections | 10 | 60 seconds | User |
| API authentication | 5 | 60 seconds | IP address |

### Headers

**Rate Limit Information Headers**:
```http
X-RateLimit-Limit: 10          # Maximum requests per window
X-RateLimit-Remaining: 7       # Remaining requests in current window
X-RateLimit-Reset: 1706355090  # Unix timestamp when window resets
```

**Rate Limit Exceeded Response**:
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 45                # Seconds until retry allowed
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1706355090
```

### Client Implementation

**Exponential Backoff** (recommended):
```python
import asyncio
import random

async def connect_with_backoff(max_retries=5):
    retries = 0
    base_delay = 1  # Start with 1 second
    
    while retries < max_retries:
        try:
            await connect_websocket()
            return  # Success
        except RateLimitError as e:
            retries += 1
            delay = min(base_delay * (2 ** retries), 60)  # Cap at 60s
            jitter = random.uniform(0, delay * 0.1)  # Add jitter
            wait_time = delay + jitter
            
            print(f"Rate limited. Retry {retries}/{max_retries} in {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        except Exception as e:
            print(f"Connection failed: {e}")
            break
    
    print(f"Failed after {max_retries} retries")
```

---

## Connection Tracking

### Concurrent Connection Limit

**Maximum**: 3 concurrent WebSocket connections per user

**Tracking**: Redis hash `ws:connections:{user_id}`

**Connection Metadata**:
```json
{
  "connection_id": "conn-abc123",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
  "connected_at": "2026-02-07T10:30:45.123456Z",
  "last_heartbeat": "2026-02-07T10:35:15.987654Z"
}
```

### Heartbeat Protocol

**Purpose**: Detect and cleanup stale connections

**Client Responsibility**:
```javascript
// Send ping every 30 seconds
setInterval(() => {
  websocket.send(JSON.dumps({type: "ping"}));
}, 30000);
```

**Server Response**:
```json
{
  "type": "pong",
  "timestamp": "2026-02-07T10:35:16.123456Z"
}
```

**Timeout**: 5 minutes (10 missed heartbeats) → connection removed

### Getting Active Connections

**Endpoint**: `GET /api/v1/websocket/connections`

**Headers**:
```http
Authorization: Bearer <JWT_TOKEN>
```

**Response**:
```json
{
  "user_id": "user-12345678",
  "active_connections": [
    {
      "connection_id": "conn-abc123",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "connected_at": "2026-02-07T10:30:45Z",
      "last_heartbeat": "2026-02-07T10:35:15Z",
      "duration_seconds": 270
    }
  ],
  "count": 1,
  "max_allowed": 3
}
```

---

## Security Events

### Event Types Logged

| Event Type | Description | Severity | Triggered By |
|------------|-------------|----------|--------------|
| `ws_auth_success` | Successful authentication | info | Step 6 (success) |
| `ws_auth_failed` | Failed authentication | high | Any step failure |
| `ws_fingerprint_mismatch` | Device fingerprint mismatch | critical | Step 3 |
| `ws_rate_limit_exceeded` | Rate limit exceeded | medium | Step 4 |
| `ws_max_connections` | Max connections exceeded | low | Step 5 |
| `ws_session_not_found` | Session missing in Redis | high | Step 2 |
| `ws_disconnect` | WebSocket disconnection | info | Connection close |

### Event Structure

```json
{
  "timestamp": "2026-02-07T10:30:45.123456Z",
  "event_type": "ws_auth_success",
  "user_id": "user-123***",
  "ip_address": "192.168.1.***",
  "metadata": {
    "connection_id": "conn-abc123",
    "latency_ms": 25.5,
    "session_id": "550e8400-***"
  },
  "severity": "info"
}
```

**Note**: User IDs and IP addresses are anonymized for privacy.

---

## Client Examples

### Python (websockets library)

**Installation**:
```bash
pip install websockets
```

**Full Example**:
```python
import asyncio
import websockets
import json
import hashlib

def generate_fingerprint():
    """Generate device fingerprint"""
    data = "192.168.1.100|Python/3.12|1920x1080"
    return hashlib.sha256(data.encode()).hexdigest()

async def authenticate_websocket():
    """Connect to WebSocket with authentication"""
    # 1. Get JWT token from login endpoint
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:8000/api/v1/auth/login', json={
            'email': 'user@example.com',
            'password': 'password123'
        }) as resp:
            data = await resp.json()
            token = data['access_token']
            session_id = data['session_id']
    
    # 2. Generate fingerprint
    fingerprint = generate_fingerprint()
    
    # 3. Connect WebSocket
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Session-ID": session_id,
        "X-Fingerprint": fingerprint
    }
    
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        print("✅ Connected successfully")
        
        # 4. Start heartbeat task
        async def heartbeat():
            while True:
                await asyncio.sleep(30)
                await websocket.send(json.dumps({"type": "ping"}))
        
        heartbeat_task = asyncio.create_task(heartbeat())
        
        # 5. Receive messages
        try:
            async for message in websocket:
                data = json.loads(message)
                print(f"📩 Received: {data}")
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed")
        finally:
            heartbeat_task.cancel()

# Run
asyncio.run(authenticate_websocket())
```

---

### JavaScript (Browser)

**Installation**: None (built-in WebSocket API)

**Full Example**:
```html
<!DOCTYPE html>
<html>
<head>
  <title>WebSocket Authentication Example</title>
</head>
<body>
  <script>
    async function generateFingerprint() {
      const data = [
        window.location.hostname,
        navigator.userAgent,
        screen.width + 'x' + screen.height
      ].join('|');
      
      const hash = await crypto.subtle.digest(
        'SHA-256',
        new TextEncoder().encode(data)
      );
      
      return Array.from(new Uint8Array(hash))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
    }
    
    async function connectWebSocket() {
      // 1. Login to get JWT token
      const loginResp = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          email: 'user@example.com',
          password: 'password123'
        })
      });
      const {access_token, session_id} = await loginResp.json();
      
      // 2. Generate fingerprint
      const fingerprint = await generateFingerprint();
      
      // 3. Connect WebSocket
      // Note: Browser WebSocket API doesn't support custom headers
      // Use query parameters as workaround (or server-side library)
      const ws = new WebSocket(
        `ws://localhost:8000/ws?token=${access_token}&session=${session_id}&fingerprint=${fingerprint}`
      );
      
      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        
        // Start heartbeat
        setInterval(() => {
          ws.send(JSON.stringify({type: 'ping'}));
        }, 30000);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('📩 Received:', data);
      };
      
      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
      };
      
      ws.onclose = (event) => {
        console.log('🔌 WebSocket closed:', event.code, event.reason);
      };
    }
    
    // Connect on page load
    connectWebSocket();
  </script>
</body>
</html>
```

---

### Rust (tokio-tungstenite)

**Installation**:
```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
tokio-tungstenite = "0.21"
futures-util = "0.3"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
reqwest = { version = "0.11", features = ["json"] }
sha2 = "0.10"
hex = "0.4"
```

**Full Example**:
```rust
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use futures_util::{SinkExt, StreamExt};
use sha2::{Sha256, Digest};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // 1. Login to get JWT token
    let client = reqwest::Client::new();
    let login_resp = client
        .post("http://localhost:8000/api/v1/auth/login")
        .json(&serde_json::json!({
            "email": "user@example.com",
            "password": "password123"
        }))
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
    
    let token = login_resp["access_token"].as_str().unwrap();
    let session_id = login_resp["session_id"].as_str().unwrap();
    
    // 2. Generate fingerprint
    let fingerprint_data = "192.168.1.100|Rust/1.70|1920x1080";
    let mut hasher = Sha256::new();
    hasher.update(fingerprint_data.as_bytes());
    let fingerprint = hex::encode(hasher.finalize());
    
    // 3. Connect WebSocket
    let url = url::Url::parse("ws://localhost:8000/ws")?;
    let request = http::Request::builder()
        .uri(url.as_str())
        .header("Authorization", format!("Bearer {}", token))
        .header("X-Session-ID", session_id)
        .header("X-Fingerprint", fingerprint)
        .body(())?;
    
    let (ws_stream, _) = connect_async(request).await?;
    println!("✅ WebSocket connected");
    
    let (mut write, mut read) = ws_stream.split();
    
    // 4. Start heartbeat task
    let write_clone = write.clone();
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(30));
        loop {
            interval.tick().await;
            let _ = write_clone.send(Message::Text(r#"{"type":"ping"}"#.into())).await;
        }
    });
    
    // 5. Receive messages
    while let Some(msg) = read.next().await {
        match msg? {
            Message::Text(text) => {
                println!("📩 Received: {}", text);
            }
            Message::Close(_) => {
                println!("🔌 Connection closed");
                break;
            }
            _ => {}
        }
    }
    
    Ok(())
}
```

---

## Testing

### Local Development

**1. Start services**:
```bash
docker-compose up -d redis vault
```

**2. Run backend**:
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

**3. Test WebSocket connection**:
```bash
# Using wscat (install: npm install -g wscat)
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
wscat -c ws://localhost:8000/ws \
  --header "Authorization: Bearer $TOKEN" \
  --header "X-Session-ID: 550e8400-e29b-41d4-a716-446655440000" \
  --header "X-Fingerprint: 5d41402abc4b2a76b9719d911017c592..."
```

### Automated Testing

**Unit Tests**:
```bash
# Run authentication tests
pytest backend/tests/test_websocket_auth.py -v

# Run security event tests
pytest backend/tests/test_security_events.py -v
```

**Load Tests**:
```bash
# Run load tests (100 concurrent connections)
bash run_load_tests.sh
```

**Integration Tests**:
```bash
# Run full integration test suite
pytest backend/tests/integration/ -v
```

---

## Troubleshooting

### Common Issues

**1. Connection Refused**

**Error**:
```
WebSocketException: ConnectionRefusedError
```

**Cause**: Backend not running or wrong URL

**Solution**:
```bash
# Check backend running
curl http://localhost:8000/health

# If not running, start it:
cd backend && uvicorn src.main:app --port 8000
```

---

**2. 401 Unauthorized: Invalid token**

**Error**:
```json
{"error": "unauthorized", "message": "Invalid token signature"}
```

**Cause**: Wrong JWT secret or token format

**Solution**:
```bash
# Get new token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Use access_token from response
```

---

**3. 403 Forbidden: Session not found**

**Error**:
```json
{"error": "forbidden", "message": "Session not found or expired"}
```

**Cause**: Session expired or Redis cleared

**Solution**:
- Log out and log back in to create new session
- Ensure Redis running: `docker ps | grep redis`

---

**4. 429 Too Many Requests**

**Error**:
```json
{"error": "rate_limit_exceeded", "metadata": {"retry_after": 45}}
```

**Cause**: Exceeded 10 connections/60 seconds

**Solution**:
- Wait `retry_after` seconds before retrying
- Implement exponential backoff in client
- Review client reconnection logic

---

**5. Max Connections Exceeded**

**Error**:
```json
{"error": "forbidden", "message": "Maximum concurrent connections exceeded"}
```

**Cause**: Already 3 active WebSocket connections

**Solution**:
- Close unused connections
- Wait 5 minutes for stale connections to timeout
- Check active connections: `GET /api/v1/websocket/connections`

---

## Best Practices

### Client Implementation

1. **Always implement heartbeat**: Send ping every 30 seconds
2. **Use exponential backoff**: Don't retry immediately on failure
3. **Handle rate limits gracefully**: Respect `retry_after` header
4. **Close unused connections**: Don't leave connections idle
5. **Implement reconnection logic**: Handle network failures
6. **Log security events**: Track authentication failures client-side

### Security

1. **Never log JWT tokens**: Tokens are sensitive credentials
2. **Use TLS in production**: `wss://` not `ws://`
3. **Validate fingerprint**: Ensure fingerprint generation consistent
4. **Rotate tokens regularly**: Refresh tokens before expiration
5. **Monitor authentication failures**: Alert on suspicious patterns

### Performance

1. **Reuse connections**: Don't create new connection for each request
2. **Batch messages**: Send multiple messages in one frame when possible
3. **Compress large payloads**: Use gzip compression for large messages
4. **Monitor latency**: Track connection establishment time

---

## Changelog

### Version 1.0 (2026-02-07)

- Initial release
- 6-step zero-trust authentication
- Rate limiting (10 connections/60s)
- Connection tracking (max 3 concurrent)
- Security event logging
- Prometheus metrics

---

## Additional Resources

- **Security Runbook**: `WEEK2_SECURITY_RUNBOOK.md`
- **Deployment Guide**: `WEEK2_DEPLOYMENT_GUIDE.md`
- **Operations Guide**: `WEEK2_OPERATIONS_GUIDE.md`
- **GitHub Repository**: https://github.com/example/amc-simulation
- **API Documentation**: https://api.example.com/docs

---

**Status**: ✅ PRODUCTION-READY  
**Maintained By**: Development Team  
**Support**: dev@example.com
