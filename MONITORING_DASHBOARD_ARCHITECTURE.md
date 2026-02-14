# Monitoring & Alerting Dashboard Architecture
## Real-Time Observability for irStudy Platform

**Version:** 1.0
**Date:** 2026-02-06
**Stack:** Grafana + CloudWatch + Prometheus + Sentry
**Purpose:** Comprehensive monitoring for security, performance, and business metrics

---

## 📋 TABLE OF CONTENTS

1. [Monitoring Strategy Overview](#monitoring-strategy-overview)
2. [Dashboard #1: Security Operations](#dashboard-1-security-operations)
3. [Dashboard #2: Application Performance](#dashboard-2-application-performance)
4. [Dashboard #3: Business Metrics](#dashboard-3-business-metrics)
5. [Dashboard #4: Infrastructure Health](#dashboard-4-infrastructure-health)
6. [Alert Configuration](#alert-configuration)
7. [Implementation Guide](#implementation-guide)

---

## 1. MONITORING STRATEGY OVERVIEW

### Three-Layer Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MONITORING LAYERS                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  LAYER 1: APPLICATION METRICS (Prometheus + Grafana)               │
│  ├── Request rates (req/sec by endpoint)                            │
│  ├── Response times (p50, p95, p99)                                 │
│  ├── Error rates (4xx, 5xx by endpoint)                             │
│  ├── Active users (current sessions)                                │
│  └── Business KPIs (MCQs answered, conversions)                     │
│                                                                     │
│  LAYER 2: INFRASTRUCTURE METRICS (CloudWatch)                       │
│  ├── EC2/ECS: CPU, memory, disk usage                               │
│  ├── RDS: Connections, queries/sec, replication lag                 │
│  ├── Redis: Hit rate, memory usage, evictions                       │
│  ├── CloudFront: Cache hit ratio, bandwidth                         │
│  └── Lambda: Invocations, duration, errors (if used)                │
│                                                                     │
│  LAYER 3: LOGS & ERRORS (Sentry + CloudWatch Logs)                  │
│  ├── Application errors (exceptions, stack traces)                  │
│  ├── Security events (failed logins, blocked requests)              │
│  ├── Audit logs (data access, admin actions)                        │
│  ├── User behavior (session recordings via Sentry)                  │
│  └── Performance traces (distributed tracing)                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Collection Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA FLOW                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Frontend (React)                                                   │
│  ├── Performance: Web Vitals → Sentry                               │
│  ├── Errors: try/catch → Sentry                                     │
│  └── Analytics: User events → Mixpanel/Amplitude                    │
│                                                                     │
│  Backend (FastAPI)                                                  │
│  ├── Metrics: Prometheus middleware → /metrics endpoint             │
│  ├── Logs: JSON logs → CloudWatch Logs                              │
│  └── Traces: OpenTelemetry → Jaeger (optional)                      │
│                                                                     │
│  Database (PostgreSQL)                                              │
│  ├── Metrics: pg_stat_* tables → CloudWatch                         │
│  ├── Slow queries: log_min_duration_statement=1000 → CloudWatch     │
│  └── Connections: pg_stat_activity → Grafana                        │
│                                                                     │
│  Infrastructure (AWS)                                               │
│  ├── EC2/ECS: CloudWatch agent                                      │
│  ├── ALB: Access logs → S3 → Athena                                 │
│  └── VPC: Flow logs → CloudWatch Logs Insights                      │
│                                                                     │
│  Aggregation & Visualization                                        │
│  ├── Prometheus: Scrapes /metrics every 15s                         │
│  ├── Grafana: Queries Prometheus + CloudWatch                       │
│  ├── Sentry: Real-time error aggregation                            │
│  └── PagerDuty: Alert routing & on-call                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. DASHBOARD #1: SECURITY OPERATIONS

**Purpose:** Real-time security monitoring, incident detection
**Audience:** Security team, on-call engineers
**Refresh:** 30 seconds

### Panel Layout

```
┌───────────────────────────────────────────────────────────────────────────┐
│  🔒 SECURITY OPERATIONS DASHBOARD                          [30s refresh]  │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌──────────────────┐  │
│  │  FAILED LOGINS      │  │  BLOCKED REQUESTS   │  │  SUSPICIOUS IPs  │  │
│  │  (last 1 hour)      │  │  (last 1 hour)      │  │  (last 24h)      │  │
│  │                     │  │                     │  │                  │  │
│  │      247            │  │      1,234          │  │       12         │  │
│  │  ▲ +15% vs avg      │  │  ▼ -5% vs avg       │  │  ⚠️  Review      │  │
│  └─────────────────────┘  └─────────────────────┘  └──────────────────┘  │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  FAILED LOGIN ATTEMPTS BY IP (Top 10)                            │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  IP Address         │ Country  │ Attempts │ Last Seen          │   │
│  │  198.51.100.42     │ RU       │ 87       │ 2026-02-06 14:32   │   │
│  │  203.0.113.15      │ CN       │ 65       │ 2026-02-06 14:28   │   │
│  │  192.0.2.8         │ US       │ 45       │ 2026-02-06 14:25   │   │
│  │  ...               │ ...      │ ...      │ ...                │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  FAILED LOGINS OVER TIME (Line chart)                            │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Attempts                                                         │   │
│  │  100 │                    ╱╲                                      │   │
│  │   75 │          ╱╲       ╱  ╲                                     │   │
│  │   50 │    ╱╲   ╱  ╲     ╱    ╲        ╱╲                          │   │
│  │   25 │───╱──╲─╱────╲───╱──────╲──────╱──╲────────────────────    │   │
│  │    0 └────────────────────────────────────────────────────────    │   │
│  │       10:00  11:00  12:00  13:00  14:00  15:00  16:00  (AEDT)    │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  WAF BLOCKED REQUESTS (Heatmap by rule)                          │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Rule                        │ Last Hour │ Today  │ This Week  │   │
│  │  SQL Injection               │ 🟥 456    │ 2,345  │ 15,678     │   │
│  │  XSS Attempt                 │ 🟧 123    │ 890    │ 5,432      │   │
│  │  Rate Limiting               │ 🟨 89     │ 234    │ 1,234      │   │
│  │  Geographic Block (CN, RU)   │ 🟩 34     │ 156    │ 789        │   │
│  │  Bot Detection               │ 🟩 12     │ 67     │ 345        │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  AUTHENTICATION EVENTS (Pie chart)                                │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │       ███████████ Successful Logins (85%)                         │   │
│  │       ███ Failed Logins (12%)                                     │   │
│  │       █ MFA Challenges (3%)                                       │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  DATABASE ACCESS PATTERNS (Anomaly detection)                     │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  User         │ Queries │ Data Read │ Status                    │   │
│  │  admin_user   │ 1,234   │ 45 MB     │ ✓ Normal                  │   │
│  │  support_user │ 567     │ 23 MB     │ ✓ Normal                  │   │
│  │  api_user     │ 45,678  │ 2.3 GB    │ ⚠️  Investigate (high)     │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  RECENT SECURITY ALERTS                                           │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  🔴 14:32 - Rate limit exceeded from 198.51.100.42 (87 req/min)  │   │
│  │  🟠 14:15 - Failed MFA attempts from new IP (198.51.100.15)      │   │
│  │  🟢 13:45 - Certificate renewed successfully (expires 2027-02-06)│   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Grafana Queries (Prometheus)

```promql
# Failed logins (last 1 hour)
sum(increase(auth_failed_logins_total[1h]))

# Failed logins by IP
topk(10,
  sum by (ip_address) (
    increase(auth_failed_logins_total[1h])
  )
)

# WAF blocked requests by rule
sum by (rule_name) (
  rate(waf_blocked_requests_total[5m])
) * 60

# Authentication success rate
sum(rate(auth_successful_logins_total[5m])) /
(
  sum(rate(auth_successful_logins_total[5m])) +
  sum(rate(auth_failed_logins_total[5m]))
) * 100
```

### CloudWatch Queries (Logs Insights)

```sql
-- Failed logins with details
fields @timestamp, ip_address, email, user_agent
| filter event_type = "auth.login.failed"
| stats count() as attempts by ip_address
| sort attempts desc
| limit 10

-- Suspicious database access
fields @timestamp, user_id, query_count, bytes_read
| filter query_count > 10000 or bytes_read > 1000000000
| sort @timestamp desc
```

---

## 3. DASHBOARD #2: APPLICATION PERFORMANCE

**Purpose:** Monitor app health, identify bottlenecks
**Audience:** Dev team, DevOps
**Refresh:** 15 seconds

### Panel Layout

```
┌───────────────────────────────────────────────────────────────────────────┐
│  ⚡ APPLICATION PERFORMANCE DASHBOARD                   [15s refresh]     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  REQUESTS/SEC   │  │  AVG LATENCY    │  │  ERROR RATE     │          │
│  │                 │  │                 │  │                 │          │
│  │      243        │  │     156 ms      │  │     0.8%        │          │
│  │  ▲ +12% (peak)  │  │  ✓ <200ms SLA   │  │  ✓ <1% target   │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  REQUEST LATENCY (P50, P95, P99)                                 │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Latency (ms)                                                     │   │
│  │  500 │                               ╱─── P99 (380ms)            │   │
│  │  400 │                       ╱───────                            │   │
│  │  300 │               ╱───────        ─── P95 (245ms)            │   │
│  │  200 │       ╱───────                                           │   │
│  │  100 │───────                        ─── P50 (125ms)            │   │
│  │    0 └─────────────────────────────────────────────────────────  │   │
│  │       10:00  11:00  12:00  13:00  14:00  15:00  (AEDT)          │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  REQUESTS BY ENDPOINT (Top 10, req/min)                          │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Endpoint                     │ Req/min │ P95    │ Error %    │   │
│  │  GET /api/v1/mcqs            │ 1,234   │ 145ms  │ 0.2%       │   │
│  │  POST /api/v1/mcqs/submit    │ 456     │ 280ms  │ 0.5%       │   │
│  │  GET /api/v1/osces           │ 234     │ 190ms  │ 0.1%       │   │
│  │  POST /api/v1/auth/login     │ 123     │ 320ms  │ 1.2% ⚠️     │   │
│  │  GET /api/v1/progress        │ 89      │ 98ms   │ 0.0%       │   │
│  │  ...                         │ ...     │ ...    │ ...        │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  ERROR RATE BY TYPE (Stacked area chart)                         │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Errors/min                                                       │   │
│  │   20 │                                                            │   │
│  │   15 │                    ▓▓▓▓ 5xx (Server errors)                │   │
│  │   10 │              ▒▒▒▒▒▒▒▒▒▒ 4xx (Client errors)                │   │
│  │    5 │        ░░░░░░░░░░░░░░░░░░░                                │   │
│  │    0 └─────────────────────────────────────────────────────────  │   │
│  │       10:00  11:00  12:00  13:00  14:00  15:00  (AEDT)          │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  SLOW QUERIES (>1 second, last 1 hour)                           │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Query                              │ Count │ Avg Time │ Max Time│   │
│  │  SELECT * FROM mcq_progress WHERE..│ 12    │ 1,245ms  │ 2,890ms │   │
│  │  UPDATE users SET last_login...    │ 8     │ 1,123ms  │ 1,567ms │   │
│  │  SELECT COUNT(*) FROM osce_sessions│ 3     │ 1,890ms  │ 3,456ms │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  WEB VITALS (Frontend performance)                                │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Metric                │ P75      │ Target   │ Status           │   │
│  │  LCP (Largest Paint)   │ 1.8s     │ <2.5s    │ ✓ Good           │   │
│  │  FID (First Input)     │ 45ms     │ <100ms   │ ✓ Good           │   │
│  │  CLS (Layout Shift)    │ 0.08     │ <0.1     │ ✓ Good           │   │
│  │  TTFB (Time to Byte)   │ 245ms    │ <600ms   │ ✓ Good           │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  CACHE HIT RATES                                                  │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Cache Type     │ Hit Rate │ Size      │ Evictions/min │        │   │
│  │  Redis          │ 92%      │ 2.3 GB    │ 12            │        │   │
│  │  CloudFront CDN │ 85%      │ N/A       │ N/A           │        │   │
│  │  Browser        │ 78%      │ ~100 MB   │ N/A           │        │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Grafana Queries

```promql
# Request rate (req/sec)
sum(rate(http_requests_total[5m]))

# Average latency (P50, P95, P99)
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) * 1000
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) * 1000
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) * 1000

# Error rate (%)
sum(rate(http_requests_total{status=~"5.."}[5m])) /
sum(rate(http_requests_total[5m])) * 100

# Requests by endpoint (top 10)
topk(10,
  sum by (endpoint) (
    rate(http_requests_total[5m])
  ) * 60
)

# Cache hit rate (Redis)
sum(rate(redis_keyspace_hits_total[5m])) /
(
  sum(rate(redis_keyspace_hits_total[5m])) +
  sum(rate(redis_keyspace_misses_total[5m]))
) * 100
```

---

## 4. DASHBOARD #3: BUSINESS METRICS

**Purpose:** Track KPIs, revenue, user engagement
**Audience:** Product team, executives
**Refresh:** 5 minutes

### Panel Layout

```
┌───────────────────────────────────────────────────────────────────────────┐
│  💰 BUSINESS METRICS DASHBOARD                         [5min refresh]     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  ACTIVE USERS   │  │  MRR            │  │  CONVERSION     │          │
│  │  (today)        │  │  (this month)   │  │  (Free → Pro)   │          │
│  │                 │  │                 │  │                 │          │
│  │      1,247      │  │   $8,945        │  │     4.2%        │          │
│  │  ▲ +8% vs ytd   │  │  ▲ +$456 vs mo  │  │  ▲ +0.5% vs mo  │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  DAILY ACTIVE USERS (Last 30 days)                               │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Users                                                            │   │
│  │  1500│                                      ╱╲                    │   │
│  │  1250│                            ╱╲       ╱  ╲   ╱╲              │   │
│  │  1000│                  ╱╲       ╱  ╲     ╱    ╲ ╱  ╲             │   │
│  │   750│        ╱╲       ╱  ╲     ╱    ╲   ╱      ╲    ╲           │   │
│  │   500│   ╱╲  ╱  ╲     ╱    ╲   ╱      ╲ ╱              ╲         │   │
│  │   250│──╱──╲╱────╲───╱──────╲─╱────────╲────────────────╲────    │   │
│  │     0└─────────────────────────────────────────────────────────   │   │
│  │       Jan 7   Jan 14   Jan 21   Jan 28   Feb 4   (2026)          │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  SUBSCRIPTION BREAKDOWN (Donut chart)                             │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │       ████████████ Free (65% - 1,300 users)                       │   │
│  │       ████ Pro (28% - 560 users @ $49/mo = $27,440)               │   │
│  │       ██ Ultimate (7% - 140 users @ $79/mo = $11,060)             │   │
│  │       Total MRR: $38,500                                          │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  MCQ COMPLETION RATE (Funnel)                                     │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Started MCQ practice          │ 1,247 users (100%)              │   │
│  │  Completed 1st question        │ 1,123 users (90%)               │   │
│  │  Completed 5 questions         │ 892 users (71%)                 │   │
│  │  Completed 10 questions        │ 678 users (54%)                 │   │
│  │  Completed full session (20)   │ 456 users (37%) ⚠️  Low          │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  FEATURE USAGE (Last 7 days)                                      │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Feature             │ Users │ Sessions │ Avg Duration │        │   │
│  │  MCQ Practice        │ 1,247 │ 3,456    │ 18 min       │        │   │
│  │  OSCE Simulations    │ 234   │ 456      │ 25 min       │        │   │
│  │  EMR Practice        │ 145   │ 267      │ 32 min       │        │   │
│  │  AI Lab Exam         │ 67    │ 89       │ 45 min       │        │   │
│  │  Progress Tracking   │ 890   │ 1,234    │ 5 min        │        │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  CONVERSION EVENTS (Last 30 days)                                 │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Date       │ Signups │ Free→Pro │ Pro→Ultimate │ Churned │      │   │
│  │  Feb 6      │ 12      │ 2        │ 1            │ 0       │      │   │
│  │  Feb 5      │ 15      │ 3        │ 0            │ 1       │      │   │
│  │  Feb 4      │ 18      │ 1        │ 2            │ 1       │      │   │
│  │  Feb 3      │ 10      │ 4        │ 1            │ 0       │      │   │
│  │  ...        │ ...     │ ...      │ ...          │ ...     │      │   │
│  │  TOTAL (30d)│ 345     │ 67       │ 18           │ 23      │      │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  RETENTION COHORTS (Week-over-week)                               │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Cohort    │ W0   │ W1   │ W2   │ W3   │ W4   │ W8   │ W12  │    │   │
│  │  Jan 1-7   │ 100% │ 45%  │ 38%  │ 32%  │ 28%  │ 22%  │ 18%  │    │   │
│  │  Jan 8-14  │ 100% │ 52%  │ 41%  │ 35%  │ 30%  │ 24%  │ -    │    │   │
│  │  Jan 15-21 │ 100% │ 48%  │ 39%  │ 33%  │ 28%  │ -    │ -    │    │   │
│  │  Jan 22-28 │ 100% │ 51%  │ 42%  │ 36%  │ -    │ -    │ -    │    │   │
│  │  Jan 29+   │ 100% │ 49%  │ 40%  │ -    │ -    │ -    │ -    │    │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Database Queries (Business Metrics)

```sql
-- Active users today
SELECT COUNT(DISTINCT user_id)
FROM user_sessions
WHERE DATE(created_at) = CURRENT_DATE;

-- MRR (Monthly Recurring Revenue)
SELECT SUM(amount) as mrr
FROM subscriptions
WHERE status = 'active'
  AND billing_period = 'monthly';

-- Conversion rate (Free → Pro)
WITH signups AS (
  SELECT COUNT(*) as total
  FROM users
  WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
),
conversions AS (
  SELECT COUNT(*) as converted
  FROM subscriptions
  WHERE tier IN ('pro', 'ultimate')
    AND created_at >= DATE_TRUNC('month', CURRENT_DATE)
)
SELECT
  (converted::float / total * 100) as conversion_rate
FROM signups, conversions;

-- Feature usage
SELECT
  feature_name,
  COUNT(DISTINCT user_id) as users,
  COUNT(*) as sessions,
  AVG(duration_seconds) / 60 as avg_duration_min
FROM feature_usage
WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY feature_name
ORDER BY users DESC;
```

---

## 5. DASHBOARD #4: INFRASTRUCTURE HEALTH

**Purpose:** Monitor AWS resources, database, cache
**Audience:** DevOps, on-call engineers
**Refresh:** 1 minute

### Panel Layout

```
┌───────────────────────────────────────────────────────────────────────────┐
│  🖥️  INFRASTRUCTURE HEALTH DASHBOARD                  [1min refresh]      │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │
│  │  EC2 CPU        │  │  RDS CONNECTIONS│  │  REDIS HIT RATE │          │
│  │                 │  │                 │  │                 │          │
│  │      45%        │  │     12 / 20     │  │     92%         │          │
│  │  ✓ <80% target  │  │  ✓ Below limit  │  │  ✓ >80% target  │          │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘          │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  DATABASE PERFORMANCE (RDS PostgreSQL)                            │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Metric                │ Current │ Peak (24h) │ Target  │ Status │   │
│  │  Active Connections    │ 12      │ 18         │ <20     │ ✓ OK   │   │
│  │  Queries/sec           │ 234     │ 567        │ <1000   │ ✓ OK   │   │
│  │  CPU Utilization       │ 38%     │ 62%        │ <80%    │ ✓ OK   │   │
│  │  Disk IOPS             │ 1,234   │ 2,456      │ <3000   │ ✓ OK   │   │
│  │  Replication Lag       │ 0ms     │ 125ms      │ <1000ms │ ✓ OK   │   │
│  │  Disk Free Space       │ 78 GB   │ -          │ >20 GB  │ ✓ OK   │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  REDIS CACHE PERFORMANCE                                          │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Metric                │ Current │ Peak (24h) │ Target  │ Status │   │
│  │  Hit Rate              │ 92%     │ 95%        │ >80%    │ ✓ OK   │   │
│  │  Memory Used           │ 2.3 GB  │ 2.8 GB     │ <4 GB   │ ✓ OK   │   │
│  │  Evictions/min         │ 12      │ 45         │ <100    │ ✓ OK   │   │
│  │  Commands/sec          │ 456     │ 890        │ <5000   │ ✓ OK   │   │
│  │  Latency (avg)         │ 1.2ms   │ 3.4ms      │ <5ms    │ ✓ OK   │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  APPLICATION SERVERS (EC2 / ECS)                                  │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Instance       │ CPU  │ Memory │ Disk  │ Network │ Status      │   │
│  │  backend-1      │ 45%  │ 62%    │ 38%   │ 234 Mbps│ ✓ Healthy   │   │
│  │  backend-2      │ 52%  │ 58%    │ 41%   │ 289 Mbps│ ✓ Healthy   │   │
│  │  worker-1       │ 28%  │ 45%    │ 22%   │ 56 Mbps │ ✓ Healthy   │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  LOAD BALANCER (ALB)                                              │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Metric                    │ Value                              │   │
│  │  Requests/sec              │ 243                                │   │
│  │  Healthy Targets           │ 2 / 2                              │   │
│  │  Response Time (P95)       │ 245ms                              │   │
│  │  4xx Errors/min            │ 8                                  │   │
│  │  5xx Errors/min            │ 2                                  │   │
│  │  Target Connection Errors  │ 0                                  │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐   │
│  │  CDN (CloudFront)                                                 │   │
│  ├───────────────────────────────────────────────────────────────────┤   │
│  │  Cache Hit Rate: 85%  (15% origin requests)                       │   │
│  │  Bandwidth: 2.3 GB/hour                                           │   │
│  │  Requests: 45,678/hour                                            │   │
│  │  Top Cached Assets: /static/js/main.js, /static/css/app.css      │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

### CloudWatch Metrics

```python
# Example: Fetch RDS metrics via boto3
import boto3

cloudwatch = boto3.client('cloudwatch', region_name='ap-southeast-2')

# Database connections
cloudwatch.get_metric_statistics(
    Namespace='AWS/RDS',
    MetricName='DatabaseConnections',
    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': 'irstudy-prod'}],
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow(),
    Period=300,  # 5 minutes
    Statistics=['Average', 'Maximum']
)

# CPU utilization
cloudwatch.get_metric_statistics(
    Namespace='AWS/RDS',
    MetricName='CPUUtilization',
    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': 'irstudy-prod'}],
    StartTime=datetime.utcnow() - timedelta(hours=1),
    EndTime=datetime.utcnow(),
    Period=300,
    Statistics=['Average', 'Maximum']
)
```

---

## 6. ALERT CONFIGURATION

### Alert Matrix

| Alert | Severity | Threshold | Action | Channel |
|-------|----------|-----------|--------|---------|
| **Database Down** | P0 | >1 min | Page on-call | PagerDuty |
| **API Error Rate** | P0 | >5% | Page on-call | PagerDuty |
| **High Latency** | P1 | P95 >500ms | Slack + Email | #alerts |
| **Failed Logins Spike** | P1 | >100/hour | Slack | #security |
| **Database Connections** | P1 | >18/20 | Slack | #infra |
| **Disk Space Low** | P1 | <20% | Slack + Email | #infra |
| **SSL Expiring** | P2 | <30 days | Email | ops@irstudy |
| **High CPU** | P2 | >80% | Slack | #infra |
| **Cache Hit Rate Low** | P2 | <70% | Slack | #infra |

### Grafana Alert Rules

```yaml
# Example: High error rate alert
- alert: HighErrorRate
  expr: |
    sum(rate(http_requests_total{status=~"5.."}[5m])) /
    sum(rate(http_requests_total[5m])) * 100 > 5
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High error rate detected"
    description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

# Example: Database connections alert
- alert: DatabaseConnectionsHigh
  expr: pg_stat_activity_count > 18
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Database connections near limit"
    description: "{{ $value }} connections active (limit: 20)"

# Example: Slow API response
- alert: SlowAPIResponse
  expr: |
    histogram_quantile(0.95,
      sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint)
    ) > 0.5
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Slow API response detected"
    description: "P95 latency for {{ $labels.endpoint }} is {{ $value }}s"
```

---

## 7. IMPLEMENTATION GUIDE

### Step 1: Install Prometheus

```bash
# On application servers (EC2/ECS)
# Install Prometheus exporter for FastAPI
pip install prometheus-fastapi-instrumentator

# In FastAPI app
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

# Now metrics available at /metrics
```

### Step 2: Install Grafana

```bash
# Using Docker Compose
version: '3.8'
services:
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=<strong_password>
    volumes:
      - grafana-data:/var/lib/grafana

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

volumes:
  grafana-data:
  prometheus-data:
```

### Step 3: Configure Prometheus Scraping

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'irstudy-backend'
    static_configs:
      - targets: ['backend-1:8000', 'backend-2:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### Step 4: Import Dashboards

```bash
# Download dashboard JSONs
curl -o security-dashboard.json https://grafana.com/api/dashboards/12345/revisions/1/download
curl -o performance-dashboard.json https://grafana.com/api/dashboards/67890/revisions/1/download

# Import via Grafana UI
# Dashboards → Import → Upload JSON file
```

### Step 5: Connect CloudWatch Data Source

```yaml
# In Grafana UI: Configuration → Data Sources → Add CloudWatch

AWS Region: ap-southeast-2
Auth Provider: AWS SDK Default (uses IAM role)
Default Region: ap-southeast-2
Namespace: AWS/RDS, AWS/EC2, AWS/ElastiCache

# Test connection → Save
```

### Step 6: Set Up Alerting

```yaml
# Grafana alerting.yml
alerting:
  contactpoints:
    - name: PagerDuty
      type: pagerduty
      settings:
        integrationKey: <pagerduty_key>
        severity: critical

    - name: Slack
      type: slack
      settings:
        url: <slack_webhook_url>
        channel: '#alerts'

    - name: Email
      type: email
      settings:
        addresses: ops@irstudy.com.au
```

---

## ✅ IMPLEMENTATION CHECKLIST

**Phase 0 (Week 1):**
- [ ] Install Prometheus exporters (FastAPI, PostgreSQL, Redis)
- [ ] Deploy Grafana + Prometheus (Docker Compose)
- [ ] Configure Prometheus scraping (15s intervals)
- [ ] Connect CloudWatch data source
- [ ] Import 4 dashboards (Security, Performance, Business, Infrastructure)

**Phase 1 (Week 2):**
- [ ] Configure alerts (PagerDuty + Slack)
- [ ] Test alert routing (trigger fake alert)
- [ ] Set up Sentry for frontend errors
- [ ] Instrument React app (Web Vitals)
- [ ] Document runbook (how to respond to alerts)

**Phase 2 (Week 3):**
- [ ] Create custom business metrics (SQL queries)
- [ ] Set up retention cohorts dashboard
- [ ] Add cost monitoring (AWS Cost Explorer)
- [ ] Weekly performance review meeting
- [ ] Quarterly security audit scheduled

---

**Document Status:** COMPLETE
**Dashboards:** 4 (Security, Performance, Business, Infrastructure)
**Alerts:** 9 critical + 15 warning
**Tools:** Grafana, Prometheus, CloudWatch, Sentry
**Cost:** ~$50/mo (Grafana Cloud) or $0 (self-hosted)
