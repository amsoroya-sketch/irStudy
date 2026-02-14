# Security Operations Runbook
## irStudy Platform - Incident Response & Daily Operations

**Version:** 1.0
**Last Updated:** 2026-02-06
**Owner:** Security Team / DevOps
**On-Call:** [Insert PagerDuty/Opsgenie rotation]

---

## 📋 TABLE OF CONTENTS

1. [Daily Security Operations](#daily-security-operations)
2. [Security Monitoring & Alerting](#security-monitoring--alerting)
3. [Incident Response Procedures](#incident-response-procedures)
4. [Common Security Incidents](#common-security-incidents)
5. [Security Tools & Access](#security-tools--access)
6. [Compliance & Audit](#compliance--audit)
7. [Emergency Contacts](#emergency-contacts)

---

## 1. DAILY SECURITY OPERATIONS

### Morning Security Checklist (Every Weekday)

**Time Required:** 15-20 minutes
**Responsible:** On-call engineer or security lead

```bash
#!/bin/bash
# daily_security_check.sh

echo "🔒 irStudy Daily Security Check - $(date)"
echo "============================================"

# 1. Check for new CVEs in dependencies
echo "\n📦 Dependency Vulnerabilities:"
cd frontend && npm audit --audit-level=high
cd ../backend && pip-audit -r requirements.txt

# 2. Review failed login attempts (last 24h)
echo "\n🚫 Failed Login Attempts (last 24h):"
psql $DATABASE_URL -c "
  SELECT
    COUNT(*) as attempts,
    ip_address,
    email
  FROM failed_logins
  WHERE created_at > NOW() - INTERVAL '24 hours'
  GROUP BY ip_address, email
  HAVING COUNT(*) >= 5
  ORDER BY COUNT(*) DESC;
"

# 3. Check for suspicious API activity
echo "\n⚠️  Suspicious API Activity:"
psql $DATABASE_URL -c "
  SELECT
    user_id,
    COUNT(*) as requests,
    endpoint
  FROM api_logs
  WHERE created_at > NOW() - INTERVAL '1 hour'
  GROUP BY user_id, endpoint
  HAVING COUNT(*) > 1000  -- Rate limit is 100/min, so 1000/h is suspicious
  ORDER BY COUNT(*) DESC
  LIMIT 10;
"

# 4. Review Sentry errors (critical only)
echo "\n🐛 Critical Errors (last 24h):"
# Query Sentry API for critical issues
curl -X GET "https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/?query=is:unresolved level:error&statsPeriod=24h" \
  -H "Authorization: Bearer $SENTRY_TOKEN" | jq '.[] | {title, culprit, count}'

# 5. Check SSL certificate expiry
echo "\n🔐 SSL Certificate Status:"
echo | openssl s_client -servername app.irstudy.com.au -connect app.irstudy.com.au:443 2>/dev/null | \
  openssl x509 -noout -dates

# 6. Verify backups completed
echo "\n💾 Database Backup Status:"
aws rds describe-db-snapshots \
  --db-instance-identifier irstudy-prod \
  --query 'DBSnapshots[0].[DBSnapshotIdentifier,SnapshotCreateTime,Status]' \
  --output table

echo "\n✅ Daily security check complete!"
```

**Action Items:**
- If critical CVEs found: Create ticket, patch within 48h
- If 5+ failed logins: Investigate IP, consider blocking
- If API abuse detected: Contact user or rate-limit
- If critical Sentry errors: Escalate to dev team
- If SSL expires <30 days: Renew certificate
- If backup failed: Investigate and re-run

---

### Weekly Security Tasks (Every Monday)

**Time Required:** 30-45 minutes

**1. Review Access Logs**

```sql
-- Users created in last 7 days
SELECT
  id,
  email,
  created_at,
  subscription_tier,
  metadata->>'signup_source' as source
FROM users
WHERE created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;

-- Subscription upgrades (fraud check)
SELECT
  user_id,
  old_tier,
  new_tier,
  payment_method,
  country,
  created_at
FROM subscription_events
WHERE event_type = 'upgraded'
  AND created_at > NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

**Red Flags:**
- Multiple signups from same IP in short time (bot/abuse)
- Upgrades from high-risk countries without 3D Secure
- Same payment method used for multiple accounts

**2. Review Security Alerts**

```bash
# Check CloudWatch security alarms
aws cloudwatch describe-alarms \
  --alarm-names "HighCPUUsage" "UnauthorizedAPIAttempts" "DatabaseConnections" \
  --query 'MetricAlarms[?StateValue==`ALARM`]' \
  --output table

# Check WAF blocked requests
aws wafv2 get-sampled-requests \
  --web-acl-id $WAF_ACL_ID \
  --rule-metric-name BlockedRequests \
  --scope CLOUDFRONT \
  --time-window Start=$(date -d '7 days ago' +%s),End=$(date +%s) \
  --max-items 100
```

**3. Update Security Dashboard**

Access Grafana/Datadog dashboard and verify:
- [ ] Metrics match expected patterns
- [ ] No unusual spikes in traffic
- [ ] Error rates within SLO (<1%)
- [ ] Response times <500ms p95

---

### Monthly Security Tasks (First Monday of Month)

**Time Required:** 2-3 hours

**1. Dependency Updates**

```bash
# Update all dependencies
cd frontend
npm update
npm audit fix
npm audit  # Verify no high/critical vulnerabilities

cd ../backend
pip list --outdated
# Manually update requirements.txt (test each upgrade)
pip-audit -r requirements.txt
```

**2. Credential Rotation**

```bash
# Rotate database password
aws rds modify-db-instance \
  --db-instance-identifier irstudy-prod \
  --master-user-password "$(openssl rand -base64 32)" \
  --apply-immediately

# Update in Secrets Manager
aws secretsmanager update-secret \
  --secret-id irstudy/db/password \
  --secret-string "new_password_here"

# Rotate Stripe API keys (every 90 days)
# 1. Create new Restricted Key in Stripe Dashboard
# 2. Update in backend/.env (via Vercel/Railway dashboard)
# 3. Test payments work with new key
# 4. Revoke old key after 24h grace period
```

**3. Access Review**

```bash
# List all users with admin/superuser access
psql $DATABASE_URL -c "
  SELECT
    email,
    role,
    last_login_at,
    created_at
  FROM users
  WHERE role IN ('admin', 'superuser')
  ORDER BY last_login_at DESC;
"

# Remove inactive admins (no login in 90 days)
# Downgrade to regular user or disable account
```

**4. Security Audit Report**

Generate monthly report:
- Failed login attempts (total, by IP)
- Blocked requests (WAF)
- Critical vulnerabilities patched
- Access changes (new admins, revoked access)
- Incidents (number, severity, time-to-resolution)

---

## 2. SECURITY MONITORING & ALERTING

### Alert Configuration

**Critical Alerts (Page on-call immediately):**

| Alert | Threshold | Action |
|-------|-----------|--------|
| Database Down | >1 minute downtime | Page on-call, failover to standby |
| API Error Rate | >5% errors | Page on-call, investigate logs |
| DDoS Attack | >10,000 req/sec | Activate Cloudflare "I'm Under Attack" mode |
| Payment Fraud | Chargeback rate >1% | Contact Stripe, review recent payments |
| Data Breach | PHI accessed by unauthorized user | IMMEDIATE: Activate incident response plan |

**Warning Alerts (Email/Slack, investigate during business hours):**

| Alert | Threshold | Action |
|-------|-----------|--------|
| Failed Login Spike | >50 failures/hour | Check logs, consider blocking IPs |
| Unusual API Usage | >1,000 req/hour from single user | Contact user, check for abuse |
| Low Disk Space | <20% free | Increase storage or clean up logs |
| SSL Expiring | <30 days | Renew certificate |
| High Error Rate | >1% errors (not critical) | Review Sentry, create bug tickets |

### Alert Channels

```yaml
# PagerDuty Integration
critical_alerts:
  - Database down
  - API error rate >5%
  - DDoS attack
  - Data breach
  routing: On-call engineer (24/7)

# Slack Integration (#alerts channel)
warning_alerts:
  - Failed login spike
  - Unusual API usage
  - Low disk space
  - SSL expiring
  - High error rate
  routing: Security team (business hours)

# Email (ops@irstudy.com.au)
informational:
  - Daily security report
  - Weekly access review
  - Monthly audit report
```

### Monitoring Dashboards

**Grafana Dashboard: Security Overview**

Panels:
1. **Failed Login Attempts (last 24h)**
   - Graph: Attempts over time
   - Table: Top 10 IPs by failure count

2. **API Rate Limits**
   - Gauge: Current req/min vs limit
   - Graph: Requests by endpoint

3. **Authentication Events**
   - Pie chart: Success vs failures
   - Timeline: Signups, logins, logouts

4. **Database Connections**
   - Graph: Active connections
   - Alert: >18/20 connections (max is 20)

5. **Stripe Payment Events**
   - Counter: Successful payments today
   - Counter: Failed payments today
   - Alert: Chargeback detected

6. **Error Rates**
   - Graph: 4xx errors (client errors)
   - Graph: 5xx errors (server errors)
   - Target: <1% combined

**Access Dashboard:**
- URL: https://grafana.irstudy.com.au/d/security
- Credentials: Stored in 1Password (ops team)

---

## 3. INCIDENT RESPONSE PROCEDURES

### Incident Severity Levels

| Severity | Definition | Response Time | Examples |
|----------|-----------|---------------|----------|
| **P0 (Critical)** | Platform down or data breach | <15 min | Database offline, PHI leak, ransomware |
| **P1 (High)** | Major feature broken or security vulnerability | <1 hour | Payments failing, auth bypass found |
| **P2 (Medium)** | Minor feature broken | <4 hours | Email notifications delayed |
| **P3 (Low)** | Cosmetic issue or enhancement | <24 hours | UI bug, typo in content |

### Incident Response Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    INCIDENT RESPONSE WORKFLOW                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. DETECT                                                          │
│     ├── Alert fires (PagerDuty, Sentry, WAF)                        │
│     ├── User reports issue (support@irstudy.com.au)                 │
│     └── Proactive monitoring (daily checks)                         │
│                                                                     │
│  2. TRIAGE (Within 15 minutes for P0)                               │
│     ├── Acknowledge alert (PagerDuty)                               │
│     ├── Assess severity (P0-P3)                                     │
│     ├── Create incident ticket (Jira/Linear)                        │
│     └── Notify stakeholders (Slack #incidents)                      │
│                                                                     │
│  3. INVESTIGATE                                                     │
│     ├── Check logs (CloudWatch, Sentry)                             │
│     ├── Review recent deployments (rollback if needed)              │
│     ├── Reproduce issue (staging environment)                       │
│     └── Identify root cause                                         │
│                                                                     │
│  4. CONTAIN (For security incidents)                                │
│     ├── Isolate affected systems                                    │
│     ├── Revoke compromised credentials                              │
│     ├── Block malicious IPs (WAF)                                   │
│     └── Preserve evidence (logs, database snapshots)                │
│                                                                     │
│  5. RESOLVE                                                         │
│     ├── Apply fix (code patch, config change)                       │
│     ├── Test fix (staging first)                                    │
│     ├── Deploy to production                                        │
│     └── Verify resolution (monitor for 1 hour)                      │
│                                                                     │
│  6. COMMUNICATE                                                     │
│     ├── Internal: Update Slack #incidents                           │
│     ├── External: Status page (status.irstudy.com.au)               │
│     ├── Users: Email notification (if affects all users)            │
│     └── Regulators: Notify OAIC if data breach (within 72h)         │
│                                                                     │
│  7. POST-MORTEM (Within 48h of resolution)                          │
│     ├── Timeline of events                                          │
│     ├── Root cause analysis (5 Whys)                                │
│     ├── Action items to prevent recurrence                          │
│     └── Share learnings (team meeting)                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Incident Communication Templates

**Internal (Slack #incidents):**

```
🚨 INCIDENT DETECTED
Severity: P0 - Critical
Time: 2026-02-06 14:32 UTC+10
Issue: Database connection pool exhausted
Impact: All users unable to load MCQs
On-call: @jane.smith
Status: Investigating

Updates:
14:35 - Identified: Max connections (20) reached
14:40 - Action: Killed 5 idle connections, investigating leak
14:45 - Resolution: Code fix deployed, connection pooling fixed
14:50 - Verified: Platform operational, monitoring for 1 hour
```

**External (Status Page):**

```
🟠 Investigating: Platform Slowness
Posted: 2026-02-06 14:35 AEDT

We are aware that some users are experiencing slow load times
for MCQ practice sessions. Our team is investigating.

Update (14:45): We have identified the issue and deployed a fix.
Service is returning to normal. We will continue monitoring.

Update (15:00): All systems operational. Thank you for your patience.

Affected Services:
- MCQ Practice: Performance degraded → Operational
- OSCE Simulations: No impact
- EMR Practice: No impact
```

**User Email (If major outage):**

```
Subject: Service Disruption - Resolved

Dear irStudy User,

We experienced a service disruption today between 14:32 - 14:50 AEDT
that prevented access to MCQ practice sessions.

The issue has been resolved and all services are operational.

As an apology for the inconvenience:
- Pro users: +3 days added to subscription
- Ultimate users: +7 days added to subscription

We have implemented measures to prevent similar issues.

For questions: support@irstudy.com.au

Regards,
irStudy Team
```

---

## 4. COMMON SECURITY INCIDENTS

### 4.1 Data Breach (P0 - Critical)

**Scenario:** Unauthorized access to user data (emails, progress, PHI if applicable)

**Immediate Actions (within 15 minutes):**

1. **Contain:**
   ```bash
   # Revoke all API keys
   stripe keys revoke sk_live_xxxxxx

   # Force logout all users (invalidate sessions)
   redis-cli FLUSHDB  # Clears all session tokens

   # Block attacker IP (if known)
   aws wafv2 update-ip-set \
     --id $WAF_IP_SET_ID \
     --addresses "192.0.2.1/32"
   ```

2. **Preserve Evidence:**
   ```bash
   # Snapshot database immediately
   aws rds create-db-snapshot \
     --db-snapshot-identifier breach-evidence-$(date +%Y%m%d-%H%M%S)

   # Export CloudWatch logs
   aws logs create-export-task \
     --log-group-name /aws/irstudy/backend \
     --from $(date -d '24 hours ago' +%s)000 \
     --to $(date +%s)000 \
     --destination s3://irstudy-security-evidence/breach-$(date +%Y%m%d)
   ```

3. **Assess Scope:**
   ```sql
   -- Identify compromised accounts
   SELECT
     user_id,
     action,
     ip_address,
     created_at
   FROM audit_logs
   WHERE ip_address = '192.0.2.1'  -- Attacker IP
     AND created_at > NOW() - INTERVAL '24 hours'
   ORDER BY created_at DESC;

   -- Check for data exfiltration
   SELECT
     user_id,
     endpoint,
     COUNT(*) as requests,
     SUM(response_size_bytes) as total_bytes
   FROM api_logs
   WHERE ip_address = '192.0.2.1'
     AND created_at > NOW() - INTERVAL '24 hours'
   GROUP BY user_id, endpoint
   HAVING COUNT(*) > 100  -- Suspicious bulk downloads
   ORDER BY total_bytes DESC;
   ```

**Within 72 Hours:**

4. **Notify Regulator (OAIC):**
   - Required by Australian Privacy Act if "likely to result in serious harm"
   - Form: https://www.oaic.gov.au/privacy/notifiable-data-breaches/submit-a-data-breach-notification
   - Include: What data, how many users, remediation steps

5. **Notify Affected Users:**
   ```
   Subject: Important Security Notice - Data Breach Notification

   Dear [Name],

   We are writing to inform you of a security incident affecting your account.

   What happened: On 2026-02-06, unauthorized access to our database occurred.

   What data was accessed:
   - Email address
   - Study progress (MCQ scores, OSCE sessions)
   - [NOT accessed: passwords (encrypted), payment info (stored by Stripe)]

   What we're doing:
   - Fixed security vulnerability
   - Enhanced monitoring
   - Offered free credit monitoring (if PHI exposed)

   What you should do:
   - Change your password immediately
   - Enable MFA (two-factor authentication)
   - Monitor for suspicious emails

   For questions: security@irstudy.com.au

   We sincerely apologize for this incident.

   irStudy Security Team
   ```

6. **Remediation:**
   - Patch vulnerability that allowed breach
   - Implement additional security controls (e.g., 2FA mandatory)
   - Hire external forensics firm (if large breach)
   - Consider cyber insurance claim

---

### 4.2 DDoS Attack (P0 - Critical)

**Symptoms:**
- Sudden spike in traffic (>10,000 req/sec)
- Legitimate users unable to access site
- High CPU/memory usage
- Database connection exhaustion

**Response:**

1. **Activate Cloudflare "Under Attack" Mode:**
   ```bash
   # Via Cloudflare API
   curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/security_level" \
     -H "Authorization: Bearer $CF_API_TOKEN" \
     -H "Content-Type: application/json" \
     --data '{"value":"under_attack"}'

   # This enables JavaScript challenge for all visitors
   ```

2. **Enable Rate Limiting (if not already):**
   ```bash
   # AWS WAF rate limiting rule
   aws wafv2 create-rate-based-rule \
     --name DDoSMitigation \
     --scope CLOUDFRONT \
     --rate-limit 100  # Requests per 5 minutes per IP
   ```

3. **Block Attack Source (if identifiable):**
   ```bash
   # If attack from specific country
   # Block via Cloudflare (e.g., block all traffic from CN, RU if not serving those markets)

   # If attack from specific IPs
   aws wafv2 update-ip-set \
     --id $WAF_IP_SET_ID \
     --addresses "198.51.100.0/24" "203.0.113.0/24"
   ```

4. **Scale Infrastructure (if needed):**
   ```bash
   # Increase backend auto-scaling limits
   aws autoscaling set-desired-capacity \
     --auto-scaling-group-name irstudy-backend-asg \
     --desired-capacity 10  # Scale from 2 to 10 instances

   # Increase database connections
   aws rds modify-db-instance \
     --db-instance-identifier irstudy-prod \
     --max-connections 50  # Increase from 20 to 50
   ```

5. **Monitor and Adjust:**
   - Watch Cloudflare analytics for attack patterns
   - Adjust rate limits based on attack type
   - Consider enabling bot protection (Cloudflare Bot Management)

**Post-Attack:**
- Review attack patterns (IPs, user-agents, request paths)
- Improve DDoS mitigation (e.g., upgrade Cloudflare plan, enable Bot Management)
- Document lessons learned

---

### 4.3 Account Takeover / Credential Stuffing (P1 - High)

**Symptoms:**
- Spike in failed login attempts from multiple IPs
- Users reporting unauthorized access to their accounts
- Unusual activity (e.g., MCQ progress reset, subscription cancellation)

**Response:**

1. **Identify Compromised Accounts:**
   ```sql
   -- Accounts with successful login from new location
   SELECT
     u.email,
     l.ip_address,
     l.country,
     l.created_at,
     u.last_login_ip
   FROM login_events l
   JOIN users u ON l.user_id = u.id
   WHERE l.success = true
     AND l.created_at > NOW() - INTERVAL '1 hour'
     AND l.ip_address != u.last_login_ip
     AND l.country != u.last_login_country;
   ```

2. **Force Password Reset:**
   ```python
   # Send forced password reset email
   for user in compromised_users:
       send_email(
           to=user.email,
           subject="Security Alert: Password Reset Required",
           body=f"""
           We detected unusual activity on your account.

           For your security, please reset your password immediately:
           {generate_password_reset_link(user.id)}

           Your account has been temporarily locked until you reset your password.

           If you did not attempt to access your account, please contact us immediately.
           """
       )

       # Lock account until password reset
       user.is_locked = True
       user.lock_reason = "Suspected credential stuffing"
       db.commit()
   ```

3. **Block Attack IPs:**
   ```bash
   # Extract IPs with high failure rate
   psql $DATABASE_URL -c "
     COPY (
       SELECT DISTINCT ip_address
       FROM login_events
       WHERE success = false
         AND created_at > NOW() - INTERVAL '1 hour'
       GROUP BY ip_address
       HAVING COUNT(*) > 100
     ) TO STDOUT
   " | while read ip; do
     aws wafv2 update-ip-set \
       --id $WAF_IP_SET_ID \
       --addresses "$ip/32"
   done
   ```

4. **Enable MFA for Affected Users:**
   ```python
   # Require MFA on next login for compromised users
   for user in compromised_users:
       user.require_mfa_on_next_login = True
       db.commit()
   ```

5. **Notify Users:**
   ```
   Subject: Security Alert - Unusual Account Activity

   We detected a login attempt on your account from an unrecognized device:

   IP: 198.51.100.42
   Location: Moscow, Russia
   Time: 2026-02-06 14:32 AEDT

   If this was you, no action needed.

   If this was NOT you:
   1. Change your password immediately
   2. Enable two-factor authentication (MFA)
   3. Review your account activity for unauthorized changes

   Your account has been temporarily locked for your protection.

   Questions: security@irstudy.com.au
   ```

---

### 4.4 Payment Fraud (P1 - High)

**Symptoms:**
- Chargeback notification from Stripe
- Multiple failed payment attempts with different cards
- Subscription upgrade from high-risk country without 3D Secure

**Response:**

1. **Review Stripe Radar:**
   ```bash
   # Check recent high-risk payments
   stripe charges list --limit 100 --outcome risk_level=highest
   ```

2. **Refund Fraudulent Payment:**
   ```bash
   # If confirmed fraud
   stripe refunds create --charge ch_xxxxxxxxxx --reason fraudulent
   ```

3. **Block Fraudulent User:**
   ```sql
   -- Suspend account
   UPDATE users
   SET
     is_suspended = true,
     suspension_reason = 'Payment fraud detected',
     suspended_at = NOW()
   WHERE id = 'user_xxxxxxxxxx';

   -- Cancel subscription
   -- (Stripe webhook will handle automatic cancellation)
   ```

4. **Enable Stripe Radar Rules:**
   ```javascript
   // In Stripe Dashboard → Radar → Rules
   // Add rules like:
   // - Block if card country != account country
   // - Require 3D Secure for payments >$50
   // - Block if IP is proxy/VPN
   // - Block if email is disposable
   ```

5. **Monitor Chargeback Rate:**
   ```python
   # If chargeback rate >1%, Stripe may suspend account
   # Monitor weekly:
   chargebacks = stripe.Dispute.list(limit=100)
   payments = stripe.Charge.list(limit=1000)

   chargeback_rate = len(chargebacks) / len(payments)

   if chargeback_rate > 0.01:
       send_alert("⚠️ Chargeback rate is {:.2%}, investigate fraud patterns")
   ```

---

## 5. SECURITY TOOLS & ACCESS

### Tool Inventory

| Tool | Purpose | Access | Cost |
|------|---------|--------|------|
| **Clerk** | Authentication | Admin Dashboard | $25/mo (Plus tier) |
| **Stripe** | Payments | Dashboard + API | 2.9% + $0.30/txn |
| **Sentry** | Error tracking | Web UI | $26/mo (Team tier) |
| **CloudWatch** | Logs & monitoring | AWS Console | ~$10/mo |
| **PagerDuty** | On-call alerting | Web + Mobile app | $21/user/mo |
| **Cloudflare** | WAF + DDoS | Dashboard | $20/mo (Pro tier) |
| **1Password** | Secrets management | Desktop + Browser | $7.99/user/mo |
| **AWS Secrets Manager** | API secrets | AWS Console + CLI | $0.40/secret/mo |

### Access Control Matrix

| Tool | Admin | DevOps | Developer | Support |
|------|-------|--------|-----------|---------|
| Clerk Dashboard | ✅ | ✅ | ❌ | ❌ |
| Stripe Dashboard | ✅ | ✅ | ❌ | Read-only |
| AWS Console | ✅ | ✅ | Read-only | ❌ |
| Production Database | ✅ (break-glass) | ❌ | ❌ | ❌ |
| Sentry | ✅ | ✅ | ✅ | ❌ |
| PagerDuty | ✅ | ✅ | ✅ | ❌ |
| 1Password (Security vault) | ✅ | ✅ | ❌ | ❌ |

**Break-Glass Access:**
- Production database: Only in emergency, requires approval from 2 admins
- Logged in CloudWatch: `SELECT * FROM admin_actions WHERE action='database_access'`

---

## 6. COMPLIANCE & AUDIT

### Compliance Checklist (Quarterly)

**Australian Privacy Act (APP) Compliance:**

- [ ] Privacy Policy published and up-to-date
- [ ] User consent obtained for data collection
- [ ] Data minimization (only collect necessary data)
- [ ] Users can access their data (export feature)
- [ ] Users can delete their data (GDPR right to erasure)
- [ ] Cross-border disclosure notice (if using US cloud)
- [ ] Data breach notification process documented (72h to OAIC)
- [ ] Privacy officer appointed (contact: privacy@irstudy.com.au)

**HIPAA Compliance (If Storing PHI):**

- [ ] Business Associate Agreements (BAA) with vendors:
  - [ ] Clerk (authentication) - BAA signed
  - [ ] Stripe (payments) - BAA signed
  - [ ] AWS (hosting) - BAA signed
- [ ] PHI encrypted at rest (AES-256) ✓
- [ ] PHI encrypted in transit (TLS 1.3) ✓
- [ ] Access logs retained for 6 years
- [ ] Annual risk assessment conducted
- [ ] Employee HIPAA training completed

**PCI DSS Compliance (Payment Card Industry):**

- [ ] SAQ A completed (Stripe handles all card data)
- [ ] No card data stored on our servers ✓
- [ ] PCI compliance attestation from Stripe obtained
- [ ] Annual self-assessment questionnaire (SAQ) submitted

### Audit Log Requirements

**What to Log:**

```python
# Audit log schema
audit_logs:
  - user_id: UUID
  - action: str  # "user.login", "mcq.submit", "subscription.upgrade"
  - resource_type: str  # "user", "mcq", "subscription"
  - resource_id: UUID
  - ip_address: str
  - user_agent: str
  - outcome: str  # "success", "failure", "unauthorized"
  - metadata: JSON  # Additional context
  - created_at: timestamp
```

**Retention:**
- Security logs: 6 years (HIPAA requirement if applicable)
- Access logs: 3 years (Australian Privacy Act)
- Payment logs: 7 years (Tax compliance)
- Application logs: 90 days (cost optimization)

**Regular Exports:**

```bash
# Export audit logs quarterly (for compliance audits)
psql $DATABASE_URL -c "
  COPY (
    SELECT *
    FROM audit_logs
    WHERE created_at BETWEEN '2026-01-01' AND '2026-03-31'
  ) TO STDOUT CSV HEADER
" > audit_logs_Q1_2026.csv

# Encrypt and store securely
gpg --encrypt --recipient compliance@irstudy.com.au audit_logs_Q1_2026.csv
aws s3 cp audit_logs_Q1_2026.csv.gpg s3://irstudy-compliance-archives/2026/Q1/
```

---

## 7. EMERGENCY CONTACTS

### Internal Team

| Role | Name | Email | Phone | Timezone |
|------|------|-------|-------|----------|
| **Security Lead** | Jane Smith | jane@irstudy.com.au | +61 4XX XXX XXX | AEDT (UTC+10) |
| **DevOps Lead** | John Doe | john@irstudy.com.au | +61 4XX XXX XXX | AEDT (UTC+10) |
| **CTO** | Alice Brown | alice@irstudy.com.au | +61 4XX XXX XXX | AEDT (UTC+10) |
| **Legal Counsel** | Bob Wilson | bob@irstudy.com.au | +61 4XX XXX XXX | AEDT (UTC+10) |

### External Vendors

| Vendor | Purpose | Support Contact | SLA |
|--------|---------|----------------|-----|
| **Clerk** | Authentication | support@clerk.com | 4h (business hours) |
| **Stripe** | Payments | support@stripe.com | 2h (24/7 for critical) |
| **AWS** | Infrastructure | AWS Support Console | 1h (Business tier) |
| **Cloudflare** | WAF/DDoS | support@cloudflare.com | 2h (Pro tier) |

### Regulatory / Legal

| Organization | Purpose | Contact | When to Contact |
|-------------|---------|---------|----------------|
| **OAIC** (Office of Australian Information Commissioner) | Data breach notification | enquiries@oaic.gov.au, +61 1300 363 992 | Within 72h of discovering data breach |
| **ACSC** (Australian Cyber Security Centre) | Cyber incident reporting | asd.assist@defence.gov.au, 1300 CYBER1 | For significant cyber attacks |
| **AFP** (Australian Federal Police) | Cybercrime reporting | cybercrime@afp.gov.au | For criminal activity (hacking, fraud) |

### Incident Escalation Path

```
Level 1: On-call Engineer
  ├── Handles: P2-P3 incidents
  └── Escalates: P0-P1 incidents within 15 min

Level 2: Security Lead / DevOps Lead
  ├── Handles: P1 incidents
  ├── Escalates: P0 incidents immediately
  └── Notifies: CTO for all P0-P1

Level 3: CTO
  ├── Handles: P0 incidents (data breach, platform down)
  ├── Coordinates: Response team
  └── Notifies: CEO, Legal Counsel if needed

Level 4: CEO / Legal Counsel
  ├── Handles: Public communication, regulatory notification
  └── Engages: External counsel, PR firm (if major breach)
```

---

## 📚 APPENDICES

### Appendix A: Security Runbook Quick Reference

```bash
# Bookmark these commands for quick access

# 1. Check recent failed logins
psql $DB_URL -c "SELECT ip_address, COUNT(*) FROM failed_logins WHERE created_at > NOW() - INTERVAL '1 hour' GROUP BY ip_address HAVING COUNT(*) > 10;"

# 2. Block an IP (WAF)
aws wafv2 update-ip-set --id $WAF_ID --addresses "192.0.2.1/32"

# 3. Force logout all users (emergency)
redis-cli FLUSHDB

# 4. Create database snapshot (preserve evidence)
aws rds create-db-snapshot --db-instance-identifier irstudy-prod --db-snapshot-identifier emergency-$(date +%Y%m%d-%H%M%S)

# 5. Export logs for investigation
aws logs create-export-task --log-group-name /aws/irstudy/backend --from $(date -d '24 hours ago' +%s)000 --to $(date +%s)000 --destination s3://irstudy-security-evidence/

# 6. Check Sentry for critical errors
curl "https://sentry.io/api/0/organizations/$SENTRY_ORG/issues/?query=is:unresolved level:error" -H "Authorization: Bearer $SENTRY_TOKEN"

# 7. Rotate database password
aws rds modify-db-instance --db-instance-identifier irstudy-prod --master-user-password "$(openssl rand -base64 32)" --apply-immediately

# 8. Enable Cloudflare "Under Attack" mode
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/settings/security_level" -H "Authorization: Bearer $CF_TOKEN" --data '{"value":"under_attack"}'

# 9. Check SSL certificate expiry
echo | openssl s_client -servername app.irstudy.com.au -connect app.irstudy.com.au:443 2>/dev/null | openssl x509 -noout -dates

# 10. Suspend a user account
psql $DB_URL -c "UPDATE users SET is_suspended = true, suspension_reason = 'Security incident' WHERE email = 'suspect@example.com';"
```

### Appendix B: Post-Mortem Template

```markdown
# Incident Post-Mortem: [Incident Title]

**Date:** 2026-02-06
**Severity:** P0 - Critical
**Duration:** 18 minutes (14:32 - 14:50 AEDT)
**Incident Lead:** Jane Smith

## Summary
[Brief 2-3 sentence description of what happened]

## Timeline (All times AEDT)
- 14:32 - Alert fired: Database connection pool exhausted
- 14:35 - On-call engineer acknowledged, began investigation
- 14:40 - Root cause identified: Connection leak in SOAP note saving
- 14:45 - Fix deployed to production
- 14:50 - Verified resolution, incident closed

## Root Cause
[Detailed explanation of why it happened]

## Impact
- Users affected: ~1,200 active users at time of incident
- Services impacted: MCQ practice sessions (unable to load)
- Services not impacted: OSCE simulations, EMR practice
- Revenue impact: ~$50 (18 min downtime × 1,200 users × $49/mo ÷ 43,200 min/mo)

## Resolution
[What was done to fix it]

## Action Items
- [ ] Fix connection leak in SOAP note service (jane, P0, done)
- [ ] Add connection pool monitoring (john, P1, 2026-02-08)
- [ ] Increase connection pool size from 20 to 30 (john, P1, 2026-02-08)
- [ ] Add alert if connections >25 (jane, P2, 2026-02-10)
- [ ] Review all database clients for similar leaks (team, P2, 2026-02-15)

## Lessons Learned
**What went well:**
- Alert fired within 30 seconds of issue
- Root cause identified quickly
- Fix deployed rapidly

**What went poorly:**
- No monitoring for connection pool exhaustion
- Connection leak not caught in code review
- No automated tests for connection cleanup

**What we'll change:**
- Mandatory: Close database connections in `finally` blocks
- Add pre-commit hook to detect missing `db.close()` calls
- Add integration test to verify connection cleanup
```

---

**Document Status:** COMPLETE
**Version:** 1.0
**Last Updated:** 2026-02-06
**Review Schedule:** Quarterly (next review: 2026-05-06)
**Owner:** Security Team
