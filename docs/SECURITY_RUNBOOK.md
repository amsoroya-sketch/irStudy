# irStudy Security Incident Response Runbook

**Project**: irStudy HIPAA-Compliant Medical Education Platform
**Version**: 1.0.0
**Last Updated**: 2026-02-02

## 1. Security Incident Classification

### P0 - Critical (15 min response)
- Data Breach: Unauthorized PHI access
- Ransomware/Malware: Active execution
- Authentication Bypass: Compromised credentials
- HIPAA Violation: PHI exposed in logs
- Database Compromise: Unauthorized access
- Cryptographic Failure: Keys exposed

### P1 - High (1 hour response)
- Privilege Escalation: Container running as root
- Weak Credentials: Default/predictable passwords
- Unpatched Vulnerability: CVE CRITICAL/HIGH
- Excessive Permissions: Over-privileged service
- Audit Trail Tampering: Logs deleted/modified
- Supply Chain Risk: Malicious dependency

### P2 - Medium (4 hour response)
- Insecure Configuration: Debug mode in production
- Incomplete Encryption: Data unencrypted at-rest
- Weak TLS: Self-signed or old TLS versions
- Insufficient Logging: Security events not captured
- Access Control Gap: Over-privileged user
- Secret Rotation Overdue: API key >90 days old

### P3 - Low (1 business day)
- Documentation Gap
- Policy Violation
- Code Quality Issue
- Deprecation Warning

## 2. Immediate Response Steps

### Step 0: Activation
- Declare incident in security channel immediately
- Identify incident lead
- Start timeline log with incident ID: INC-YYYYMMDD-HHMMSS
- Do NOT: Delete logs, shutdown containers, modify DB without backup

### Step 1: Containment (Data Breach)
Preserve evidence - DO NOT modify files

### Step 2: Investigation
Collect logs with timestamps to /evidence/INC-*/

### Step 3: Notification
Escalate to CISO and legal within 15 minutes for P0

## 3. Post-Incident Review
- Document timeline
- Analyze root cause
- Create preventive actions
- Add detective controls
- Schedule verification

## 4. Security Scanning
- GitLeaks: Detect hardcoded secrets
- Trivy: Scan Docker images
- Bandit: Python code security
- Safety: Dependency vulnerabilities

## 5. Checklists

### P0 Response
- [ ] Declare incident
- [ ] Preserve evidence
- [ ] Collect logs
- [ ] Revoke credentials
- [ ] Rotate secrets
- [ ] Verify services
- [ ] Notify CISO (15 min)
- [ ] Schedule PIR (24h)

### HIPAA Breach Notification
- [ ] Determine scope
- [ ] Notify individuals (60 days)
- [ ] Notify media (>500)
- [ ] Notify HHS/State AG
- [ ] Document all notifications
- [ ] Update compliance log

## References
- HIPAA Breach: 45 CFR 164.400-414
- HIPAA Security: 45 CFR 164.308-318
- NIST: https://www.nist.gov/cyberframework
- Docker: https://docs.docker.com/engine/security/

**Status**: APPROVED FOR PRODUCTION
**Last Review**: 2026-02-02
