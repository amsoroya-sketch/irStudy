# Expert Agents Infrastructure
## Implementation Guide for 46-Agent System

**Last Updated:** December 14, 2025
**Purpose:** Infrastructure setup for multi-agent orchestration

**Status:** Base classes complete ✅ | 45 agents to implement ⏳

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Agent Registry & Discovery](#agent-registry--discovery)
3. [Inter-Agent Communication](#inter-agent-communication)
4. [Agent State Management](#agent-state-management)
5. [Agent Monitoring](#agent-monitoring)
6. [Agent Testing Framework](#agent-testing-framework)
7. [Agent Deployment](#agent-deployment)
8. [Implementation Roadmap](#implementation-roadmap)

---

## Overview

### Current Status

**✅ Complete:**
- `BaseAgent` class (src/agents/base_agent.py)
- `PM-001` Project Manager (src/agents/pm_001_project_manager.py)
- 3 LangGraph workflows (src/agents/workflows/orchestration.py)
- Agent specifications (docs/AGENT_SPECIFICATIONS.md)

**⏳ To Implement:**
- 45 remaining agents (DEV-001 to MED-015)
- Agent registry system
- Inter-agent message queue
- Agent state persistence
- Monitoring dashboards
- Testing infrastructure

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PM-001 (Coordinator)                  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Agent Registry                         │
│  (Service Discovery + Agent Metadata)                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Message Queue (Redis Pub/Sub)               │
│         (Inter-Agent Communication)                      │
└─────────────────────────────────────────────────────────┘
                            ↓
┌───────────┬─────────────┬──────────────┬───────────────┐
│ DEV-001   │  AI-001     │  DEVOPS-001  │   QA-001      │
│ to        │  to         │  to          │   to          │
│ DEV-012   │  AI-008     │  DEVOPS-006  │   QA-004      │
│           │             │              │               │
│ MED-001   │             │              │               │
│ to        │             │              │               │
│ MED-015   │             │              │               │
└───────────┴─────────────┴──────────────┴───────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                 State Store (PostgreSQL + Redis)         │
│            (Agent State + Task History)                  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Monitoring (Prometheus + Grafana)           │
│      (Agent Performance + Task Metrics)                  │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Agent Registry & Discovery

**Purpose:** Central registry for all 46 agents with service discovery

### Database Schema

Create `src/agents/registry/schema.sql`:

```sql
-- Agent Registry Table
CREATE TABLE agent_registry (
    agent_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'offline',  -- online, offline, busy, error
    host VARCHAR(255),
    port INTEGER,
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB  -- capabilities, technologies, etc.
);

-- Agent Capabilities Table
CREATE TABLE agent_capabilities (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(20) REFERENCES agent_registry(agent_id),
    capability VARCHAR(100) NOT NULL,
    proficiency_level INTEGER CHECK (proficiency_level >= 1 AND proficiency_level <= 10)
);

-- Agent Load Table (for load balancing)
CREATE TABLE agent_load (
    agent_id VARCHAR(20) REFERENCES agent_registry(agent_id),
    current_tasks INTEGER DEFAULT 0,
    max_tasks INTEGER DEFAULT 3,
    avg_task_duration_sec FLOAT,
    total_tasks_completed INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agent_status ON agent_registry(status);
CREATE INDEX idx_agent_role ON agent_registry(role);
```

### Agent Registry Service

Create `src/agents/registry/registry_service.py`:

```python
#!/usr/bin/env python3
"""
Agent Registry Service
Central service discovery and registration for all 46 agents
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncpg
import uvicorn

app = FastAPI(title="Agent Registry Service")

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None

class AgentRegistration(BaseModel):
    agent_id: str
    name: str
    role: str
    host: str
    port: int
    metadata: Dict[str, Any]

class AgentStatus(BaseModel):
    agent_id: str
    status: str  # online, offline, busy, error

@app.on_event("startup")
async def startup():
    """Initialize database connection pool"""
    global db_pool
    db_pool = await asyncpg.create_pool(
        host="localhost",
        port=5432,
        user="postgres",
        password="postgres",
        database="medical_ai"
    )

@app.on_event("shutdown")
async def shutdown():
    """Close database connection pool"""
    await db_pool.close()

@app.post("/api/agents/register")
async def register_agent(agent: AgentRegistration):
    """
    Register a new agent with the registry.

    Example:
        POST /api/agents/register
        {
          "agent_id": "DEV-001",
          "name": "Senior Backend Architect",
          "role": "backend_dev",
          "host": "localhost",
          "port": 6001,
          "metadata": {"technologies": ["FastAPI", "SQLAlchemy"]}
        }
    """
    async with db_pool.acquire() as conn:
        # Insert or update agent registration
        await conn.execute("""
            INSERT INTO agent_registry (agent_id, name, role, status, host, port, last_heartbeat, metadata)
            VALUES ($1, $2, $3, 'online', $4, $5, NOW(), $6)
            ON CONFLICT (agent_id)
            DO UPDATE SET
                status = 'online',
                host = $4,
                port = $5,
                last_heartbeat = NOW(),
                metadata = $6
        """, agent.agent_id, agent.name, agent.role, agent.host, agent.port, agent.metadata)

    return {"status": "registered", "agent_id": agent.agent_id}

@app.post("/api/agents/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str):
    """
    Update agent heartbeat to show it's still alive.

    Agents should send heartbeat every 30 seconds.
    """
    async with db_pool.acquire() as conn:
        result = await conn.execute("""
            UPDATE agent_registry
            SET last_heartbeat = NOW(), status = 'online'
            WHERE agent_id = $1
        """, agent_id)

        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="Agent not found")

    return {"status": "ok"}

@app.get("/api/agents")
async def list_agents(role: Optional[str] = None, status: Optional[str] = None):
    """
    List all registered agents.

    Filters:
        - role: Filter by agent role (backend_dev, ai_engineer, etc.)
        - status: Filter by status (online, offline, busy)
    """
    async with db_pool.acquire() as conn:
        query = "SELECT * FROM agent_registry WHERE 1=1"
        params = []

        if role:
            params.append(role)
            query += f" AND role = ${len(params)}"

        if status:
            params.append(status)
            query += f" AND status = ${len(params)}"

        rows = await conn.fetch(query, *params)

        agents = []
        for row in rows:
            agents.append({
                "agent_id": row['agent_id'],
                "name": row['name'],
                "role": row['role'],
                "status": row['status'],
                "host": row['host'],
                "port": row['port'],
                "last_heartbeat": row['last_heartbeat'].isoformat() if row['last_heartbeat'] else None,
                "metadata": row['metadata']
            })

        return {"agents": agents, "total": len(agents)}

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get specific agent details"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT * FROM agent_registry WHERE agent_id = $1
        """, agent_id)

        if not row:
            raise HTTPException(status_code=404, detail="Agent not found")

        return {
            "agent_id": row['agent_id'],
            "name": row['name'],
            "role": row['role'],
            "status": row['status'],
            "host": row['host'],
            "port": row['port'],
            "last_heartbeat": row['last_heartbeat'].isoformat() if row['last_heartbeat'] else None,
            "metadata": row['metadata']
        }

@app.post("/api/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: AgentStatus):
    """Update agent status (online, offline, busy, error)"""
    async with db_pool.acquire() as conn:
        await conn.execute("""
            UPDATE agent_registry
            SET status = $2
            WHERE agent_id = $1
        """, agent_id, status.status)

    return {"status": "updated"}

@app.get("/api/agents/discover/{role}")
async def discover_agents_by_role(role: str, max_load: int = 3):
    """
    Discover available agents by role with load balancing.

    Returns agents that:
    - Match the requested role
    - Are online
    - Have capacity (current_tasks < max_tasks)

    Sorted by current load (least busy first).
    """
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT r.*, l.current_tasks, l.max_tasks
            FROM agent_registry r
            JOIN agent_load l ON r.agent_id = l.agent_id
            WHERE r.role = $1
              AND r.status = 'online'
              AND l.current_tasks < l.max_tasks
            ORDER BY l.current_tasks ASC
        """, role)

        agents = []
        for row in rows:
            agents.append({
                "agent_id": row['agent_id'],
                "name": row['name'],
                "current_tasks": row['current_tasks'],
                "max_tasks": row['max_tasks'],
                "load_percentage": (row['current_tasks'] / row['max_tasks']) * 100
            })

        return {"agents": agents, "available_count": len(agents)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5100)
```

---

## 2. Inter-Agent Communication

**Purpose:** Message queue for agents to communicate

### Using Redis Pub/Sub

Create `src/agents/messaging/message_queue.py`:

```python
#!/usr/bin/env python3
"""
Agent Message Queue
Redis Pub/Sub for inter-agent communication
"""

import redis
import json
from typing import Dict, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class AgentMessage:
    """Message format for inter-agent communication"""
    from_agent: str
    to_agent: str
    message_type: str  # task_request, task_response, notification, etc.
    payload: Dict[str, Any]
    timestamp: str = None
    correlation_id: str = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class AgentMessageQueue:
    """
    Message queue for agent communication using Redis Pub/Sub.

    Usage:
        queue = AgentMessageQueue()

        # Agent sends message
        queue.send_message("DEV-001", "PM-001", "task_complete", {"task_id": "123"})

        # Agent subscribes to messages
        queue.subscribe("PM-001", callback_function)
    """

    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()

    def send_message(self, from_agent: str, to_agent: str, message_type: str, payload: Dict[str, Any]):
        """
        Send a message from one agent to another.

        Args:
            from_agent: Sender agent ID
            to_agent: Recipient agent ID
            message_type: Type of message
            payload: Message data
        """
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload
        )

        # Publish to agent's channel
        channel = f"agent:{to_agent}"
        self.redis_client.publish(channel, json.dumps(asdict(message)))

    def broadcast_message(self, from_agent: str, message_type: str, payload: Dict[str, Any]):
        """
        Broadcast message to all agents.

        Args:
            from_agent: Sender agent ID
            message_type: Type of message
            payload: Message data
        """
        message = AgentMessage(
            from_agent=from_agent,
            to_agent="ALL",
            message_type=message_type,
            payload=payload
        )

        # Publish to broadcast channel
        self.redis_client.publish("agent:broadcast", json.dumps(asdict(message)))

    def subscribe(self, agent_id: str, callback: Callable[[AgentMessage], None]):
        """
        Subscribe to messages for this agent.

        Args:
            agent_id: Agent ID to subscribe for
            callback: Function to call when message received
        """
        # Subscribe to agent-specific channel
        self.pubsub.subscribe(f"agent:{agent_id}")

        # Also subscribe to broadcast channel
        self.pubsub.subscribe("agent:broadcast")

        # Listen for messages
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    msg_data = json.loads(message['data'])
                    agent_message = AgentMessage(**msg_data)

                    # Filter: only process messages for this agent or broadcasts
                    if agent_message.to_agent == agent_id or agent_message.to_agent == "ALL":
                        callback(agent_message)
                except Exception as e:
                    print(f"Error processing message: {e}")

# Example usage
if __name__ == "__main__":
    queue = AgentMessageQueue()

    # Callback function
    def handle_message(message: AgentMessage):
        print(f"Received from {message.from_agent}: {message.message_type}")
        print(f"Payload: {message.payload}")

    # Agent PM-001 subscribes to messages
    queue.subscribe("PM-001", handle_message)
```

### Integration with BaseAgent

Update `src/agents/base_agent.py` to include messaging:

```python
class BaseAgent(ABC):
    def __init__(self, metadata: AgentMetadata):
        # ... existing code ...

        # Message queue
        from .messaging.message_queue import AgentMessageQueue
        self.message_queue = AgentMessageQueue()

    def send_message(self, to_agent: str, message_type: str, payload: Dict[str, Any]):
        """Send message to another agent"""
        self.message_queue.send_message(
            from_agent=self.metadata.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload
        )
        self.logger.info(f"Sent message to {to_agent}: {message_type}")

    def start_listening(self):
        """Start listening for messages"""
        def handle_message(message):
            self.logger.info(f"Received message: {message.message_type} from {message.from_agent}")
            self.handle_incoming_message(message)

        self.message_queue.subscribe(self.metadata.agent_id, handle_message)

    def handle_incoming_message(self, message):
        """Override in subclass to handle messages"""
        pass
```

---

## 3. Agent State Management

**Purpose:** Persist agent state across restarts

### State Store Schema

```sql
-- Agent State Table
CREATE TABLE agent_state (
    agent_id VARCHAR(20) PRIMARY KEY,
    state JSONB NOT NULL,  -- Agent-specific state
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Task History Table
CREATE TABLE task_history (
    task_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(20) REFERENCES agent_registry(agent_id),
    task_title VARCHAR(500),
    task_description TEXT,
    status VARCHAR(20),  -- pending, in_progress, completed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result JSONB,
    error TEXT
);

CREATE INDEX idx_task_agent ON task_history(agent_id);
CREATE INDEX idx_task_status ON task_history(status);
```

### State Manager

Create `src/agents/state/state_manager.py`:

```python
#!/usr/bin/env python3
"""Agent State Manager"""

import asyncpg
import json
from typing import Dict, Any, Optional

class AgentStateManager:
    """
    Manage persistent state for agents.

    Features:
    - Save agent state to PostgreSQL
    - Load agent state on startup
    - Task history tracking
    """

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def save_state(self, agent_id: str, state: Dict[str, Any]):
        """Save agent state"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO agent_state (agent_id, state, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (agent_id)
                DO UPDATE SET state = $2, updated_at = NOW()
            """, agent_id, json.dumps(state))

    async def load_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent state"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT state FROM agent_state WHERE agent_id = $1
            """, agent_id)

            if row:
                return json.loads(row['state'])
            return None

    async def save_task(self, task_data: Dict[str, Any]):
        """Save task to history"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO task_history
                (agent_id, task_title, task_description, status, started_at)
                VALUES ($1, $2, $3, $4, NOW())
            """, task_data['agent_id'], task_data['title'],
                task_data['description'], task_data['status'])

    async def update_task(self, task_id: str, status: str, result: Optional[Dict] = None, error: Optional[str] = None):
        """Update task status"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                UPDATE task_history
                SET status = $2,
                    result = $3,
                    error = $4,
                    completed_at = CASE WHEN $2 IN ('completed', 'failed') THEN NOW() ELSE NULL END
                WHERE task_id = $1
            """, task_id, status, json.dumps(result) if result else None, error)
```

---

## 4. Agent Monitoring

**Purpose:** Monitor agent health and performance

### Prometheus Metrics

Create `src/agents/monitoring/metrics.py`:

```python
#!/usr/bin/env python3
"""Agent Monitoring Metrics"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Agent metrics
agent_tasks_total = Counter(
    'agent_tasks_total',
    'Total tasks processed by agent',
    ['agent_id', 'status']
)

agent_task_duration = Histogram(
    'agent_task_duration_seconds',
    'Task execution duration',
    ['agent_id']
)

agent_active_tasks = Gauge(
    'agent_active_tasks',
    'Number of currently active tasks',
    ['agent_id']
)

agent_errors = Counter(
    'agent_errors_total',
    'Total errors encountered',
    ['agent_id', 'error_type']
)

# Start Prometheus metrics server
start_http_server(9200)
```

### Grafana Dashboard

Create `docker/grafana/dashboards/agent_metrics.json`:

```json
{
  "dashboard": {
    "title": "Agent System Metrics",
    "panels": [
      {
        "title": "Tasks by Agent",
        "targets": [
          {
            "expr": "sum(agent_tasks_total) by (agent_id)"
          }
        ]
      },
      {
        "title": "Task Duration (p95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, agent_task_duration_seconds)"
          }
        ]
      },
      {
        "title": "Active Tasks",
        "targets": [
          {
            "expr": "sum(agent_active_tasks) by (agent_id)"
          }
        ]
      }
    ]
  }
}
```

---

## 5. Agent Testing Framework

**Purpose:** Test agents before deployment

### Mock Agent for Testing

Create `tests/agents/mock_agent.py`:

```python
#!/usr/bin/env python3
"""Mock Agent for Testing"""

from src.agents import BaseAgent, AgentMetadata, AgentRole, AgentTask
from typing import Dict, Any, List

class MockAgent(BaseAgent):
    """Mock agent for testing workflows"""

    def __init__(self, agent_id: str, responses: Dict[str, Any] = None):
        metadata = AgentMetadata(
            agent_id=agent_id,
            name=f"Mock Agent {agent_id}",
            role=AgentRole.BACKEND_DEV,
            experience_years=10,
            technologies=["Mock"],
            specializations=["Testing"],
            pros=["Fast", "Predictable"],
            cons=["Not real"]
        )
        super().__init__(metadata)

        self.responses = responses or {}
        self.received_tasks = []

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Return predefined response"""
        self.received_tasks.append(task)

        # Return predefined response or default success
        response_key = task.title
        if response_key in self.responses:
            return self.responses[response_key]

        return {
            'status': 'success',
            'output': {'mock': True, 'task': task.title}
        }

    def validate_output(self, task: AgentTask, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Always pass validation in mock"""
        return True, []
```

### Agent Unit Tests

Create `tests/agents/test_base_agent.py`:

```python
#!/usr/bin/env python3
"""Unit tests for BaseAgent"""

import pytest
from src.agents import AgentTask, TaskStatus
from tests.agents.mock_agent import MockAgent

def test_agent_can_accept_task():
    """Test agent task capacity"""
    agent = MockAgent("TEST-001")

    # Agent should be able to accept tasks
    assert agent.can_accept_task() == True

    # Assign max tasks
    for i in range(agent.metadata.max_concurrent_tasks):
        task = AgentTask(title=f"Task {i}", description="Test")
        agent.assign_task(task)

    # Should not accept more
    assert agent.can_accept_task() == False

def test_agent_executes_task():
    """Test agent task execution"""
    agent = MockAgent("TEST-001", responses={
        "Test Task": {"status": "success", "result": 42}
    })

    task = AgentTask(title="Test Task", description="Run test")
    completed_task = agent.run_task(task)

    assert completed_task.status == TaskStatus.COMPLETED
    assert completed_task.result['result'] == 42

def test_agent_validation_failure():
    """Test agent validation failure"""
    class FailingAgent(MockAgent):
        def validate_output(self, task, output):
            return False, ["Validation failed"]

    agent = FailingAgent("TEST-002")
    task = AgentTask(title="Test", description="Test")
    completed_task = agent.run_task(task)

    assert completed_task.status == TaskStatus.FAILED
    assert "Validation failed" in completed_task.error
```

---

## 6. Agent Deployment

**Purpose:** Deploy agents as Docker containers or processes

### Docker Deployment

Create `docker/agents/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Environment variables
ENV AGENT_ID=""
ENV AGENT_PORT=6000

# Run agent
CMD ["python", "-m", "src.agents.agent_runner"]
```

### Agent Runner

Create `src/agents/agent_runner.py`:

```python
#!/usr/bin/env python3
"""Agent Runner - Starts agent as standalone service"""

import os
import sys
import asyncio
from fastapi import FastAPI
import uvicorn

# Get agent ID from environment
AGENT_ID = os.getenv("AGENT_ID")
AGENT_PORT = int(os.getenv("AGENT_PORT", 6000))

if not AGENT_ID:
    print("Error: AGENT_ID environment variable not set")
    sys.exit(1)

# Import agent class dynamically
agent_module = f"src.agents.{AGENT_ID.lower().replace('-', '_')}"
agent_class_name = AGENT_ID.replace("-", "") + "Agent"

try:
    module = __import__(agent_module, fromlist=[agent_class_name])
    AgentClass = getattr(module, agent_class_name)
except ImportError:
    print(f"Error: Could not import {agent_class_name} from {agent_module}")
    sys.exit(1)

# Create agent instance
agent = AgentClass()

# Create FastAPI app for agent
app = FastAPI(title=f"{agent.metadata.name} API")

@app.post("/task")
async def execute_task(task_data: dict):
    """Execute a task"""
    from src.agents import AgentTask
    task = AgentTask(**task_data)
    result = agent.run_task(task)
    return {"task_id": result.task_id, "status": result.status.value}

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy", "agent_id": agent.metadata.agent_id}

@app.get("/status")
async def status():
    """Agent status"""
    return agent.get_status_report()

if __name__ == "__main__":
    print(f"Starting {agent.metadata.name} on port {AGENT_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=AGENT_PORT)
```

### Docker Compose for Agents

Add to `docker-compose.yml`:

```yaml
services:
  # ... existing services ...

  agent-dev-001:
    build: ./docker/agents
    container_name: agent_dev_001
    environment:
      - AGENT_ID=DEV-001
      - AGENT_PORT=6001
    ports:
      - "6001:6001"
    depends_on:
      - postgres
      - redis

  agent-ai-001:
    build: ./docker/agents
    container_name: agent_ai_001
    environment:
      - AGENT_ID=AI-001
      - AGENT_PORT=6002
    ports:
      - "6002:6002"
    depends_on:
      - qdrant
      - redis

  # Add more agents as needed...
```

---

## 7. Implementation Roadmap

### Week 1-2: Core Infrastructure

**Tasks:**
- [x] BaseAgent class (complete)
- [x] PM-001 implementation (complete)
- [ ] Agent Registry Service
- [ ] Message Queue system
- [ ] State Management
- [ ] Testing framework

**Deliverables:**
- Agent registry running on port 5100
- Redis Pub/Sub for messaging
- PostgreSQL schema for state
- Mock agents for testing

### Week 3-4: First 5 Agents

**Priority agents to implement:**
1. **AI-001:** RAG System Architect
2. **DEV-001:** Backend Architect
3. **DEV-002:** Frontend Architect
4. **QA-001:** Medical QA Specialist
5. **MED-001:** Cardiology Expert

**Tasks per agent:**
- Create agent class (inherit from BaseAgent)
- Implement execute_task()
- Implement validate_output()
- Write unit tests
- Deploy as Docker container
- Register with registry

### Week 5-8: Next 15 Agents

**Implement remaining DEV and AI agents:**
- DEV-003 to DEV-012 (10 agents)
- AI-002 to AI-008 (7 agents)

### Week 9-12: DevOps & QA Agents

**Implement:**
- DEVOPS-001 to DEVOPS-006 (6 agents)
- QA-002 to QA-004 (3 agents)

### Week 13-16: Medical Expert Agents

**Implement:**
- MED-002 to MED-015 (14 agents)

---

## 📊 Summary

**Infrastructure Components:**
1. ✅ Agent Registry (service discovery, load balancing)
2. ✅ Message Queue (Redis Pub/Sub for inter-agent communication)
3. ✅ State Management (PostgreSQL for persistence)
4. ✅ Monitoring (Prometheus + Grafana dashboards)
5. ✅ Testing Framework (mock agents, unit tests)
6. ✅ Deployment (Docker containers, agent runner)

**Implementation Status:**
- ✅ Base infrastructure designed
- ✅ PM-001 implemented
- ⏳ 45 agents to implement
- ⏳ Registry service to deploy
- ⏳ Monitoring dashboards to create

**Next Steps:**
1. Deploy Agent Registry Service
2. Implement first 5 priority agents
3. Test complete workflow (MCQ generation)
4. Scale to remaining 40 agents

---

**Last Updated:** December 14, 2025
**Status:** Infrastructure designed, ready for implementation 🚀
