# Legal Compliance Checklist for irStudy Commercialization

## Pre-Launch Requirements

### 1. Business Entity & IP (2-3 weeks)

| Task | Priority | Status | Notes |
|------|----------|--------|-------|
| Register business entity (Pty Ltd) | 🔴 CRITICAL | ☐ | Use ASIC online |
| Register business name | 🔴 CRITICAL | ☐ | If different from company name |
| Trademark application | 🟡 HIGH | ☐ | "irStudy" or new brand |
| Domain registration | 🔴 CRITICAL | ☐ | Secure .com and .com.au |
| Business bank account | 🟡 HIGH | ☐ | Separate from personal |
| Business insurance | 🟡 HIGH | ☐ | PI insurance recommended |

### 2. Legal Documents (1-2 weeks)

| Document | Purpose | Required By | Status |
|----------|---------|-------------|--------|
| **Terms of Service** | User agreement | Launch | ☐ |
| **Privacy Policy** | Data handling (APP 1) | Launch | ☐ |
| **Cookie Policy** | Cookie consent | Launch | ☐ |
| **Refund Policy** | Consumer protection | Launch | ☐ |
| **Copyright Notice** | IP protection | Launch | ☐ |
| **Acceptable Use Policy** | Prohibited activities | Launch | ☐ |
| **Data Processing Agreement** | If using subprocessors | Launch | ☐ |

#### Terms of Service - Essential Clauses

```
□ License Grant (limited, non-transferable)
□ Prohibited Activities (scraping, sharing accounts)
□ Intellectual Property (you own content)
□ User Content (they own their data)
□ Payment Terms (auto-renewal, refunds)
□ Termination (both parties' rights)
□ Limitation of Liability (cap at amount paid)
□ Indemnification (user protects you)
□ Governing Law (NSW, Australia)
□ Dispute Resolution (arbitration clause)
□ Medical Disclaimer (not medical advice)
□ No Guarantee (exam success not guaranteed)
```

#### Privacy Policy - APP Requirements

```
APP 1 - Open and Transparent Management:
□ How to contact you
□ How to access/correct personal info
□ How to complain

APP 3 - Collection of Solicited Personal Info:
□ What you collect (name, email, usage data)
□ Why you collect it
□ How it's collected

APP 5 - Notification:
□ Collection notice at point of collection
□ Privacy policy link

APP 6 - Use/Disclosure:
□ Primary purpose (service provision)
□ Secondary purposes (analytics, marketing)
□ Disclosure to third parties (Stripe, etc.)

APP 11 - Security:
□ Security measures description
□ Data breach procedures

APP 12 - Access:
□ How users request their data
□ Response timeframe

APP 13 - Correction:
□ How users correct data
```

### 3. Regulatory Compliance

#### AHPRA/Medical Regulatory

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Medical disclaimer on all pages | Banner + footer | ☐ |
| No guarantee of exam passage | Clear statement | ☐ |
| Not medical advice disclaimer | On content pages | ☐ |
| No AHPRA/AMC logo usage | Audit all materials | ☐ |
| Substantiation for claims | Document pass rates | ☐ |

#### Australian Consumer Law

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| Accurate pricing | No hidden fees | ☐ |
| Clear refund policy | 7-day money-back | ☐ |
| Cooling-off disclosure | Before purchase | ☐ |
| Subscription renewal notice | 7 days prior email | ☐ |
| Cancellation process | Easy online | ☐ |
| Contact information | Valid email/phone | ☐ |

### 4. Data Protection

#### Technical Measures

| Measure | Implementation | Status |
|---------|----------------|--------|
| TLS 1.3 in transit | SSL certificate | ✅ |
| AES-256 at rest | PostgreSQL encryption | ✅ |
| Password hashing | bcrypt with salt | ✅ |
| API rate limiting | 1000 req/hour/user | ☐ |
| Input validation | SQL injection prevention | ✅ |
| XSS protection | Output encoding | ☐ |
| CSRF tokens | Form submissions | ☐ |

#### Administrative Measures

| Measure | Implementation | Status |
|---------|----------------|--------|
| Access control matrix | RBAC defined | ☐ |
| Staff confidentiality agreements | If hiring | ☐ |
| Data breach response plan | Documented | ☐ |
| Privacy impact assessment | Documented | ☐ |
| Data retention schedule | Documented | ☐ |
| Secure deletion procedures | Documented | ☐ |

#### Notifiable Data Breaches (NDB) Scheme

```
Breach Assessment:
□ Is there unauthorized access/disclosure?
□ Is personal information involved?
□ Is serious harm likely?

If YES to all:
□ Investigate breach
□ Contain breach
□ Assess risk of harm
□ Notify OAIC within 72 hours
□ Notify affected individuals
□ Notify if cannot contact individuals
□ Document all actions
```

### 5. Payment Compliance

| Requirement | Provider | Status |
|-------------|----------|--------|
| PCI-DSS compliance | Stripe (they handle it) | ✅ |
| GST registration | ATO | ☐ |
| GST on invoices | If >$75K/year | ☐ |
| Tax invoices | For all payments | ☐ |
| Refund processing | Within policy timeframe | ☐ |
| Failed payment handling | Dunning management | ☐ |

---

## Post-Launch Ongoing Compliance

### Monthly

| Task | Responsible | Status |
|------|-------------|--------|
| Review access logs | Admin | ☐ |
| Update security patches | Dev | ☐ |
| Check SSL certificate expiry | Dev | ☐ |
| Review privacy complaints | Admin | ☐ |

### Quarterly

| Task | Responsible | Status |
|------|-------------|--------|
| Privacy policy review | Legal | ☐ |
| Terms of service review | Legal | ☐ |
| Security audit | Dev | ☐ |
| Data retention cleanup | Dev | ☐ |
| Staff training (if applicable) | Admin | ☐ |

### Annually

| Task | Responsible | Status |
|------|-------------|--------|
| Comprehensive legal review | Lawyer | ☐ |
| Penetration testing | Security firm | ☐ |
| Privacy impact assessment | Admin | ☐ |
| Insurance review | Admin | ☐ |
| Trademark renewal (if needed) | Legal | ☐ |

---

## Intellectual Property Audit

### Content Ownership Verification

| Content Type | Source | License | Action Required |
|--------------|--------|---------|-----------------|
| MCQs | AI-generated | Original | ✅ Register copyright |
| OSCEs | AI-generated | Original | ✅ Register copyright |
| Medical images | Various | Check each | ⚠️ Audit licenses |
| Textbook citations | Fair use | Attribution | ✅ Proper citations |
| Cochrane content | Open access | CC BY | ✅ Attribution |
| StatPearls content | Open access | CC BY | ✅ Attribution |
| Code/libraries | Open source | Various | ✅ LICENSE file |

### Recommended Copyright Notice

```
© 2026 [Company Name]. All rights reserved.

The content on this platform, including but not limited to MCQs, 
OSCE scenarios, explanations, and study materials, is protected 
by copyright and other intellectual property laws.

Unauthorized reproduction, distribution, or scraping of content 
is strictly prohibited and may result in legal action.

Medical content citations are used under fair use for educational 
purposes. Original textbooks remain property of their respective 
copyright holders.
```

---

## Accessibility Compliance (WCAG 2.1)

### Level A Requirements

| Criterion | Implementation | Status |
|-----------|----------------|--------|
| Text alternatives for images | Alt tags | ☐ |
| Keyboard accessible | Tab navigation | ☐ |
| Captions/transcripts | For video content | ☐ |
| Color not only means | Additional indicators | ☐ |
| Auto-play audio control | User can stop | ☐ |

### Level AA Requirements

| Criterion | Implementation | Status |
|-----------|----------------|--------|
| Contrast ratio 4.5:1 | Design audit | ☐ |
| Text resize 200% | Responsive design | ☐ |
| Consistent navigation | Standard layout | ☐ |
| Error identification | Clear messages | ☐ |
| Focus visible | Visible outlines | ☐ |

---

## Marketing Compliance

### Australian Consumer Law - Advertising

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| No misleading claims | "Best" claims substantiated | ☐ |
| No false testimonials | Real users only | ☐ |
| Clear pricing | Total price displayed | ☐ |
| Disclosure of commercial relationships | Sponsored content labeled | ☐ |
| Unsubscribe option | All marketing emails | ☐ |
| Spam Act compliance | Consent-based marketing | ☐ |

### Prohibited Claims Checklist

```
❌ CANNOT CLAIM:
□ "Guaranteed to pass AMC"
□ "90% pass rate" (unless verified)
□ "Official AMC preparation" (not affiliated)
□ "AHPRA approved" (not approved)
□ Medical advice or diagnosis
□ Replace formal education

✅ CAN CLAIM:
□ "Comprehensive question bank"
□ "RAG-validated citations"
□ "Used by X candidates" (if true)
□ "Based on AMC blueprint"
□ "Educational supplement"
```

---

## International Considerations

### If Targeting International Users

| Country/Region | Regulation | Requirements |
|----------------|------------|--------------|
| **EU/EEA** | GDPR | Consent, right to erasure, DPO |
| **UK** | UK GDPR | Similar to EU GDPR |
| **California** | CCPA | Disclosure, opt-out |
| **Canada** | PIPEDA | Consent, accountability |
| **Singapore** | PDPA | Consent, DPO |

### Recommendation

**Phase 1**: Block EU/UK signups to avoid GDPR complexity
```python
# Implementation
RESTRICTED_COUNTRIES = ['EU', 'UK', 'CA']  # Phase 1

@auth.route('/register')
def register():
    user_country = get_country_from_ip(request.remote_addr)
    if user_country in RESTRICTED_COUNTRIES:
        return "Service not available in your region", 403
    # Continue registration
```

**Phase 2**: Implement full GDPR compliance for international expansion

---

## Insurance Requirements

### Recommended Coverage

| Type | Coverage | Purpose | Est. Cost |
|------|----------|---------|-----------|
| Professional Indemnity | $2M | Content errors, bad advice | $2,000/year |
| Cyber Liability | $1M | Data breach, hacking | $1,500/year |
| Public Liability | $10M | Physical premises (if any) | $500/year |
| Business Insurance | $50K | Equipment, interruption | $1,000/year |

---

## Documentation Requirements

### Required Records

| Record | Retention Period | Format |
|--------|------------------|--------|
| User accounts | 7 years after deletion | Database |
| Payment transactions | 7 years | Stripe dashboard |
| Privacy complaints | 7 years | PDF |
| Data breach records | Permanent | PDF |
| Terms of Service versions | Permanent | PDF |
| Security audit reports | 7 years | PDF |
| Accessibility testing | 3 years | PDF |

---

## Emergency Contacts

| Situation | Contact | Action |
|-----------|---------|--------|
| Data breach | OAIC: 1300 363 992 | Report within 72 hours |
| Legal emergency | [Lawyer name] | Immediate consultation |
| Cyber incident | ACSC: 1300 CYBER1 | Report and guidance |
| Consumer complaint | ACCC | Respond to complaint |
| Trademark infringement | IP Australia | Enforcement action |

---

## Sign-off

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Business Owner | | | |
| Legal Advisor | | | |
| Technical Lead | | | |
| Privacy Officer | | | |

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-04  
**Review Date**: 2027-02-04

*Note: This checklist is for guidance only. Consult with qualified legal professionals for advice specific to your situation.*
