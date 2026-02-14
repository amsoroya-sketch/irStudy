# Multi-Device Architecture Decisions - AMC Prep Platform

## Executive Summary

This document outlines architecture choices for a medical education platform supporting:
- **Web** (desktop & mobile browsers)
- **iOS** & **Android** native apps
- **Optional**: Desktop apps (Windows/Mac)

**Key Requirements:**
- Offline study capability (commute, poor connectivity)
- Real-time sync across devices
- Subscription enforcement
- Content protection (prevent scraping)
- Low latency (<200ms API response)

---

## 1. High-Level Architecture Patterns

### Option A: Traditional Client-Server (REST)
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Web App   │     │  Mobile App │     │   Desktop   │
│   (SPA)     │     │  (Native)   │     │   (PWA)     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │ HTTPS/REST
                           ▼
              ┌────────────────────────┐
              │     API Gateway        │
              │   (Kong/AWS/Azure)     │
              └───────────┬────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────┐      ┌─────────┐      ┌──────────┐
   │  Auth   │      │  MCQ    │      │ Progress │
   │ Service │      │ Service │      │ Service  │
   └─────────┘      └─────────┘      └──────────┘
```

**Pros:**
- Simple, well-understood
- Easy caching
- Works everywhere

**Cons:**
- Real-time sync requires polling
- Offline support needs complex local storage
- Multiple API versions to maintain

**Best for:** Simple apps, MVPs

---

### Option B: Backend-for-Frontend (BFF) - RECOMMENDED
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Web App   │     │  Mobile App │     │   Desktop   │
│   (Next.js) │     │  (Native)   │     │   (Tauri)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │ GraphQL/REST      │ REST/GraphQL      │ REST
       ▼                   ▼                   ▼
  ┌─────────┐        ┌─────────┐        ┌─────────┐
  │Web BFF  │        │Mobile   │        │Desktop  │
  │(Next.js │        │BFF      │        │BFF      │
  │API)     │        │         │        │         │
  └────┬────┘        └────┬────┘        └────┬────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │ gRPC/Internal API
                           ▼
              ┌────────────────────────┐
              │    Core Services       │
              │ (Auth, MCQ, Billing)   │
              └────────────────────────┘
```

**Pros:**
- Optimized APIs per device type
- Mobile can have lighter payloads
- Web can have SSR for SEO
- Easier to version independently

**Cons:**
- More services to maintain
- Duplicated business logic risk

**Best for:** Multi-device apps with different UX needs

---

### Option C: Event-Driven with CQRS
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Clients   │────▶│  API Gateway │────▶│  Command   │
│ (All types) │     │              │     │  Service   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼ Write
                                        ┌─────────────┐
                                        │  PostgreSQL │
                                        │  (Primary)  │
                                        └──────┬──────┘
                                               │
                                               ▼ Events
                                        ┌─────────────┐
                                        │    Kafka    │
                                        │   /Redis    │
                                        └──────┬──────┘
                                               │
                          ┌────────────────────┼────────────────────┐
                          │                    │                    │
                          ▼                    ▼                    ▼
                   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
                   │ Read Model  │      │  Analytics  │      │   Search    │
                   │  (CQRS)     │      │   Service   │      │  (Qdrant)   │
                   └─────────────┘      └─────────────┘      └─────────────┘
```

**Pros:**
- Excellent for real-time sync
- Scales reads independently
- Great audit trail

**Cons:**
- Complex to implement
- Eventual consistency challenges
- Overkill for early-stage

**Best for:** Scale >10K users, complex sync requirements

---

## 2. Client Architecture Decisions

### 2.1 Web Application

#### Decision: Next.js 14 (App Router) vs React SPA

| Criteria | Next.js 14 | React SPA (Vite) |
|----------|-----------|------------------|
| SEO | ✅ Excellent | ❌ Poor |
| Initial Load | ✅ Fast (SSR) | ⚠️ Slower |
| API Routes | ✅ Built-in | ❌ Separate server |
| Hosting Cost | $20/mo (Vercel) | $5/mo (CDN) |
| Offline Support | ⚠️ Complex | ✅ Easier (PWA) |
| Learning Curve | Moderate | Low |

**Recommendation: Next.js 14**
- SEO matters for "AMC exam prep" search traffic
- API routes simplify backend
- Edge functions for auth checks

#### Web Architecture Pattern
```typescript
// app/layout.tsx - Root with auth
export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const user = await getUser() // Server-side auth check
  
  return (
    <html>
      <body>
        <AuthProvider user={user}>
          <SubscriptionGate tier={user?.tier}>
            {children}
          </SubscriptionGate>
        </AuthProvider>
      </body>
    </html>
  )
}

// app/study/[specialty]/page.tsx - MCQ page
export default async function StudyPage({
  params: { specialty }
}: {
  params: { specialty: string }
}) {
  // Server-side data fetch with caching
  const questions = await fetchMCQs(specialty, { 
    cache: 'force-cache',
    next: { revalidate: 3600 } // 1 hour
  })
  
  return <MCQSession questions={questions} />
}
```

---

### 2.2 Mobile Applications

#### Decision: React Native vs Flutter vs Native

| Criteria | React Native | Flutter | Native (Swift/Kotlin) |
|----------|-------------|---------|----------------------|
| Dev Speed | ✅ Fast | ✅ Fast | ❌ Slower |
| Performance | Good | ✅ Excellent | ✅ Excellent |
| UI Consistency | Platform-native | Custom (Material) | Platform-native |
| Team Size | 2 devs | 2 devs | 4 devs |
| AMC Market | iOS-heavy | Split | - |
| Offline Support | ✅ Good | ✅ Good | ✅ Excellent |

**Recommendation: React Native (Expo)**
- Your team likely knows React
- Faster to market
- Expo EAS for CI/CD
- Can eject if needed later

**Alternative: Flutter**
- Better for complex animations
- Single language (Dart)
- Consider if you have UI-heavy OSCE simulator

#### Mobile Architecture Pattern
```typescript
// Mobile app structure (React Native + Expo)
src/
├── api/                    # API clients
│   ├── client.ts          # Axios/fetch setup
│   ├── interceptors.ts    # Auth, error handling
│   └── endpoints/         # API endpoints
├── components/            # Reusable UI
├── features/              # Feature-based modules
│   ├── auth/
│   ├── mcqs/
│   ├── progress/
│   └── subscription/
├── hooks/                 # Custom React hooks
├── navigation/            # React Navigation
├── services/             # Business logic
│   ├── offline-sync.ts   # Sync engine
│   ├── analytics.ts      # Usage tracking
│   └── notifications.ts  # Push notifications
├── store/                # Zustand/Redux
└── utils/                # Helpers

// Key Mobile Features
interface MobileApp {
  // Offline-first architecture
  offlineStorage: {
    mcqs: SQLiteDatabase;        // 1000+ questions cached
    progress: AsyncStorage;       // Study sessions
    images: FileSystem;           // Offline images
  };
  
  // Background sync
  sync: {
    queueOfflineAction: (action: Action) => void;
    processQueue: () => Promise<void>;
    conflictResolution: 'server-wins' | 'client-wins' | 'merge';
  };
  
  // Push notifications
  notifications: {
    dailyReminder: LocalNotification;
    streakAtRisk: PushNotification;
    newContent: PushNotification;
  };
}
```

---

### 2.3 Desktop Application (Optional)

#### Decision: Tauri vs Electron

| Criteria | Tauri (Rust) | Electron |
|----------|-------------|----------|
| Bundle Size | ✅ ~3MB | ⚠️ ~150MB |
| Memory Usage | ✅ Low | ⚠️ High |
| Security | ✅ Excellent | Good |
| Native APIs | ✅ Full access | Good |
| Development | Rust learning curve | Just Node.js |

**Recommendation: Tauri**
- Medical students have various laptops (some old)
- Small bundle size matters
- Security is critical

#### Desktop Use Cases
- Full-screen focused study mode
- Download entire specialty for offline
- Export study reports (PDF)
- Integration with Anki (flashcards)

---

## 3. Backend Architecture Decisions

### 3.1 API Style: REST vs GraphQL vs gRPC

| Use Case | Recommendation | Reason |
|----------|---------------|--------|
| Web client | GraphQL | Flexible queries, reduce over-fetching |
| Mobile client | REST + GraphQL | REST for simple, GraphQL for complex |
| Internal services | gRPC | Performance, type safety |
| Webhooks | REST | Industry standard |

**Hybrid Approach (Recommended):**
```
Clients
  ├── Web: GraphQL (Apollo Client)
  ├── Mobile: REST for MCQs, GraphQL for progress
  └── Desktop: Same as Web

Internal
  └── gRPC between microservices
```

### 3.2 Database Strategy

#### Primary Database: PostgreSQL
- ACID compliance for user data, subscriptions
- JSONB for flexible MCQ metadata
- Full-text search for content discovery

#### Caching Strategy: Redis (Multi-tier)
```
Layer 1: CDN (Cloudflare) - Static assets, MCQ content
Layer 2: Redis - Session storage, rate limits, hot data
Layer 3: Application cache - Computed aggregations
Layer 4: Database - Source of truth
```

#### Data Partitioning Strategy
```sql
-- Partition progress table by user_id (hash)
-- Reason: User queries are isolated, easy to shard

CREATE TABLE user_progress (
    id UUID,
    user_id UUID,
    question_id VARCHAR,
    created_at TIMESTAMP
) PARTITION BY HASH (user_id);

-- Create 16 partitions for 1M users
CREATE TABLE user_progress_p0 PARTITION OF user_progress
    FOR VALUES WITH (MODULUS 16, REMAINDER 0);
-- ... p1 through p15
```

### 3.3 Service Architecture: Monolith vs Microservices

**Decision Matrix:**

| Team Size | Traffic | Recommendation |
|-----------|---------|---------------|
| 1-3 devs | <10K users | Monolith (FastAPI) |
| 4-8 devs | 10K-100K | Modular Monolith |
| 9+ devs | >100K | Microservices |

**Your Case: Modular Monolith (Best Balance)**
```
backend/
├── app/
│   ├── api/               # API layer (FastAPI routers)
│   ├── domain/            # Business logic
│   │   ├── auth/
│   │   ├── mcqs/
│   │   ├── subscriptions/
│   │   └── progress/
│   ├── infrastructure/    # External services
│   │   ├── database.py
│   │   ├── cache.py
│   │   ├── queue.py
│   │   └── storage.py
│   └── main.py
```

**Why not microservices yet:**
- Operational complexity too high for small team
- Network latency adds up (medical students expect instant)
- Debugging harder across services

**When to split:**
- AI Tutor service (separate scaling needs)
- Analytics service (different query patterns)
- Billing service (security isolation)

---

## 4. Synchronization Architecture

### Challenge: Multi-device Study Sessions

**Scenario:**
1. User studies 20 MCQs on phone during commute
2. Gets home, opens laptop
3. Expects to see updated progress immediately

### Solution: Event Sourcing + CQRS

```typescript
// Event types
interface Events {
  'mcq.answered': {
    userId: string;
    questionId: string;
    answer: string;
    isCorrect: boolean;
    timeSpent: number;
    deviceId: string;
    timestamp: Date;
  };
  
  'progress.sync-requested': {
    userId: string;
    deviceId: string;
    lastSyncTimestamp: Date;
  };
  
  'subscription.changed': {
    userId: string;
    oldTier: string;
    newTier: string;
    timestamp: Date;
  };
}

// Sync flow
class SyncEngine {
  async sync(userId: string, deviceId: string) {
    // 1. Get events since last sync
    const events = await this.eventStore.getEvents(
      userId, 
      lastSyncTime
    );
    
    // 2. Apply to local state
    for (const event of events) {
      await this.applyEvent(event);
    }
    
    // 3. Push local changes
    const localEvents = await this.getUnsyncedEvents(deviceId);
    await this.eventStore.append(userId, localEvents);
    
    // 4. Broadcast to other devices
    await this.pubsub.publish(`user:${userId}:sync`, {
      deviceId,  // Exclude sender
      timestamp: Date.now()
    });
  }
}
```

### Conflict Resolution
```typescript
// When same question answered on two devices
interface ConflictResolver {
  // Strategy 1: Last write wins (simple)
  lastWriteWins: (events: Event[]) => Event;
  
  // Strategy 2: Merge (for partial progress)
  merge: (local: Event, remote: Event) => Event;
  
  // Strategy 3: Manual (rare conflicts)
  promptUser: (conflict: Conflict) => Promise<Resolution>;
}

// For AMC prep: Use "last write wins" + audit log
// Keep both answers in history, show most recent as primary
```

---

## 5. Offline-First Architecture

### Why Critical for Your Product
- Medical students study on trains, buses
- Hospital WiFi is often poor
- International students have limited data

### Offline Strategy by Feature

| Feature | Offline Support | Sync Strategy |
|---------|----------------|---------------|
| MCQ Practice | ✅ Full | Pre-download 100-500 questions |
| AI Tutor | ❌ No | Requires internet |
| Progress Tracking | ✅ Full | Queue, sync when online |
| OSCE Videos | ⚠️ Optional | Download on WiFi |
| Analytics | ⚠️ Cached | Daily sync |

### Implementation: Service Worker (Web) + SQLite (Mobile)

```typescript
// Web: Service Worker with Workbox
// sw.ts
import { precacheAndRoute } from 'workbox-precaching';
import { NetworkFirst, CacheFirst } from 'workbox-strategies';

// Pre-cache core MCQs
precacheAndRoute(self.__WB_MANIFEST);

// Runtime caching
registerRoute(
  '/api/mcqs/*',
  new NetworkFirst({
    cacheName: 'mcq-cache',
    plugins: [
      {
        // Cache 1000 most recent questions
        cacheWillUpdate: async ({ response }) => {
          const cache = await caches.open('mcq-cache');
          const keys = await cache.keys();
          if (keys.length > 1000) {
            await cache.delete(keys[0]); // LRU eviction
          }
          return response;
        }
      }
    ]
  })
);

// Mobile: SQLite with WatermelonDB (React Native)
import { Database } from '@nozbe/watermelondb';

const database = new Database({
  adapter: {
    schema: appSchema,
    dbName: 'amc-prep',
  },
  modelClasses: [MCQ, Progress, User],
  actionsEnabled: true,
});

// Sync with server
await database.sync({
  pullChanges: async ({ lastPulledAt }) => {
    const response = await fetch(`/sync?since=${lastPulledAt}`);
    return response.json();
  },
  pushChanges: async ({ changes }) => {
    await fetch('/sync', {
      method: 'POST',
      body: JSON.stringify(changes)
    });
  }
});
```

---

## 6. Real-Time Features

### Use Cases
- Study buddy live collaboration
- Live leaderboards
- Admin announcements
- Subscription status changes

### Technology Choice: WebSockets vs Server-Sent Events vs Polling

| Feature | Technology | Reason |
|---------|-----------|--------|
| Live collaboration | WebSockets | Bidirectional |
| Notifications | SSE | One-way, simpler |
| Progress sync | Polling | Every 30s, less complex |
| Urgent alerts | Push (FCM/APNs) | Works when app closed |

### Implementation
```typescript
// Socket.io for real-time features
// server.ts
import { Server } from 'socket.io';

const io = new Server(server, {
  cors: { origin: process.env.CLIENT_URL }
});

// Auth middleware
io.use(async (socket, next) => {
  const token = socket.handshake.auth.token;
  const user = await verifyToken(token);
  socket.userId = user.id;
  socket.join(`user:${user.id}`); // Personal room
  next();
});

io.on('connection', (socket) => {
  // Study session collaboration
  socket.on('join-study-session', (sessionId) => {
    socket.join(`session:${sessionId}`);
  });
  
  // Sync events
  socket.on('progress-update', (data) => {
    // Broadcast to user's other devices
    socket.to(`user:${socket.userId}`).emit('sync-needed');
  });
});

// client.ts
const socket = io(API_URL, {
  auth: { token: getAccessToken() }
});

socket.on('sync-needed', () => {
  syncEngine.sync(); // Pull latest changes
});
```

---

## 7. Security Architecture

### Multi-Device Security Challenges

| Challenge | Solution |
|-----------|----------|
| Token theft | Short-lived access tokens (15min), refresh tokens (7 days) |
| Device lost | Remote logout, device management page |
| Session hijacking | Device fingerprinting, IP anomaly detection |
| Content scraping | Rate limiting, watermarking, bot detection |
| Subscription sharing | Max 3 devices, concurrent session limits |

### Device Management
```typescript
interface DeviceManager {
  // Track user devices
  async registerDevice(userId: string, deviceInfo: {
    deviceId: string;
    name: string;        // "John's iPhone"
    type: 'web' | 'ios' | 'android' | 'desktop';
    lastActive: Date;
    ipAddress: string;
  }): Promise<void>;
  
  // Enforce limits
  async enforceDeviceLimit(userId: string, maxDevices: number): Promise<void> {
    const devices = await this.getUserDevices(userId);
    if (devices.length >= maxDevices) {
      // Remove oldest device
      await this.revokeDevice(devices[0].deviceId);
    }
  }
  
  // User can manage devices
  async listDevices(userId: string): Promise<Device[]>;
  async revokeDevice(userId: string, deviceId: string): Promise<void>;
}
```

---

## 8. Deployment Architecture

### Environment Strategy
```
Development (Local)
  └── Docker Compose (all services)

Staging (Cloud)
  └── Single server, small DB
  └── Automated deploy on PR merge

Production (Cloud)
  ├── Multi-region (Australia primary, CDN global)
  ├── Auto-scaling (2-10 servers)
  ├── Database: Managed PostgreSQL (RDS/Cloud SQL)
  ├── Redis: Managed (ElastiCache/Memorystore)
  └── Backup: Daily automated + 30-day retention
```

### Hosting Options Comparison

| Provider | Best For | Cost (Start) | Cost (Scale) |
|----------|----------|--------------|--------------|
| **Vercel + Railway** | Speed of development | $20/mo | $200/mo |
| **AWS** | Enterprise, compliance | $100/mo | $500/mo |
| **Google Cloud** | ML/AI features | $80/mo | $400/mo |
| **Fly.io** | Global edge deployment | $30/mo | $150/mo |

**Recommendation for Your Case:**
- **Start**: Vercel (frontend) + Railway (backend) + Supabase (DB)
- **Scale**: AWS with managed services (RDS, ElastiCache)

### Infrastructure as Code
```hcl
# terraform/main.tf - Example
resource "aws_ecs_service" "api" {
  name            = "amc-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = 2
  
  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
  }
}

resource "aws_rds_cluster" "postgres" {
  cluster_identifier  = "amc-postgres"
  engine             = "aurora-postgresql"
  database_name      = "amc_prep"
  master_username    = "admin"
  master_password    = var.db_password
  
  serverlessv2_scaling_configuration {
    min_capacity = 0.5
    max_capacity = 16
  }
}
```

---

## 9. Monitoring & Observability

### Three Pillars

```typescript
// 1. Metrics (Prometheus + Grafana)
interface Metrics {
  // Business metrics
  activeUsers: Gauge;           // By tier, by device
  mcqsAnswered: Counter;        // Per minute
  subscriptionConversion: Gauge; // Free -> Paid rate
  
  // Technical metrics
  apiLatency: Histogram;        // p50, p95, p99
  errorRate: Counter;           // By endpoint
  cacheHitRate: Gauge;          // Redis performance
}

// 2. Logging (Structured JSON)
interface LogEntry {
  timestamp: string;
  level: 'info' | 'warn' | 'error';
  message: string;
  context: {
    userId?: string;
    deviceId?: string;
    requestId: string;
    endpoint: string;
    duration: number;
  };
}

// 3. Tracing (OpenTelemetry)
interface Trace {
  traceId: string;
  spans: [
    { name: 'GET /api/mcqs', duration: 45 },
    { name: 'db.query', duration: 12 },
    { name: 'cache.get', duration: 2 },
    { name: 'qdrant.search', duration: 25 }
  ];
}
```

### Alerting Rules
```yaml
# Critical alerts (PagerDuty/Slack)
- alert: HighErrorRate
  expr: error_rate > 0.01  # 1% error rate
  for: 5m
  
- alert: DatabaseConnectionsHigh
  expr: pg_connections > 80
  
- alert: PaymentFailuresSpike
  expr: stripe_failed_payments > 10
  
# Warning alerts (Slack only)
- alert: SlowAPI
  expr: api_p95_latency > 500ms
  
- alert: LowCacheHitRate
  expr: cache_hit_rate < 0.8
```

---

## 10. Decision Summary Matrix

| Decision | Choice | Alternative | Rationale |
|----------|--------|-------------|-----------|
| **Web Framework** | Next.js 14 | React SPA | SEO, SSR, API routes |
| **Mobile** | React Native (Expo) | Flutter | Team expertise, speed |
| **Desktop** | Skip initially | Tauri | Low priority, web sufficient |
| **API Style** | GraphQL (web) + REST (mobile) | gRPC | Flexibility vs simplicity |
| **Backend** | Modular Monolith | Microservices | Team size, speed |
| **Database** | PostgreSQL + Redis | MongoDB | ACID, mature ecosystem |
| **Sync Strategy** | Event sourcing | CRUD | Audit trail, offline support |
| **Offline Storage** | Service Worker (web) / SQLite (mobile) | IndexedDB | Capacity, reliability |
| **Hosting** | Vercel + Railway | AWS | Cost, simplicity |
| **Auth** | Clerk | Auth0/Custom | Speed, features |
| **Payments** | Stripe | PayPal | Industry standard |

---

## 11. Architecture Evolution Roadmap

### Phase 1: MVP (Months 1-3)
- Single Next.js app (frontend + API routes)
- Supabase (auth + database)
- Static MCQ delivery (no personalization)
- No offline support

### Phase 2: Multi-Device (Months 4-6)
- Separate FastAPI backend
- React Native mobile app
- Basic offline (cache last 100 questions)
- Device sync (polling every 30s)

### Phase 3: Scale (Months 7-12)
- CQRS for analytics
- Redis for caching
- CDN for global content
- Real-time sync (WebSockets)

### Phase 4: Enterprise (Year 2)
- Microservices (billing, AI tutor)
- Multi-region deployment
- White-label support
- Advanced analytics

---

**Next Steps:**
1. Validate these decisions with your team
2. Create proof-of-concept for top 3 riskiest choices
3. Document final decisions in Architecture Decision Records (ADRs)
