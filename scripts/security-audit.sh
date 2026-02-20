#!/bin/bash
# Security Audit Script - Run before commits
# Enforces zero-tolerance security policy
# Reference: constraints/3-security.md

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔒 Security Audit - irStudy Medical Education Platform${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

VIOLATIONS=0
PROJECT_ROOT="/home/dev/Development/irStudy"

# ============================================================================
# 1. SCAN FOR HARDCODED CREDENTIALS
# ============================================================================
echo -e "${YELLOW}[1/7] Checking for hardcoded credentials...${NC}"

# Check for Anthropic API keys in code (exclude test files)
API_KEY_FOUND=$(grep -r "sk-ant-api" "$PROJECT_ROOT/backend/src/" "$PROJECT_ROOT/frontend/src/" --include="*.py" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "test_" | grep -v "#" | wc -l || echo 0)
if [ "$API_KEY_FOUND" -gt 0 ]; then
    echo -e "${RED}❌ CRITICAL: Anthropic API key found in code${NC}"
    grep -r "sk-ant-api" "$PROJECT_ROOT/backend/src/" "$PROJECT_ROOT/frontend/src/" --include="*.py" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "test_" | grep -v "#" | head -3
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo -e "${GREEN}✅ No hardcoded API keys${NC}"
fi

# Check for JWT secrets (exclude config files that use os.getenv)
JWT_SECRET_FOUND=$(grep -r "SECRET_KEY.*=" "$PROJECT_ROOT/backend/src/" --include="*.py" 2>/dev/null | grep -v "os.getenv" | grep -v "settings" | grep -v "config.py" | grep -v "#" | wc -l || echo 0)
if [ "$JWT_SECRET_FOUND" -gt 0 ]; then
    echo -e "${RED}❌ CRITICAL: Hardcoded JWT secret found${NC}"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo -e "${GREEN}✅ No hardcoded JWT secrets${NC}"
fi

echo ""

# ============================================================================
# 2. SCAN FOR PHI (Protected Health Information) LEAKS
# ============================================================================
echo -e "${YELLOW}[2/7] Checking for PHI leaks in logs/errors...${NC}"

# Check for patient names in print/console.log statements
PHI_LOG_FOUND=$(grep -r "print.*patient.*name\|console\.log.*patient.*name" "$PROJECT_ROOT/backend/src/" "$PROJECT_ROOT/frontend/src/" --include="*.py" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "# PHI anonymized" | grep -v "anonymize" | grep -v "test_" | wc -l || echo 0)
if [ "$PHI_LOG_FOUND" -gt 0 ]; then
    echo -e "${RED}⚠️  WARNING: Potential PHI in logging statements${NC}"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo -e "${GREEN}✅ No patient names in logs${NC}"
fi

echo ""

# ============================================================================
# 3. CHECK VAULT INTEGRATION
# ============================================================================
echo -e "${YELLOW}[3/7] Verifying Vault secret management...${NC}"

if [ -f "$PROJECT_ROOT/backend/src/core/vault.py" ]; then
    echo -e "${GREEN}✅ Vault integration file exists${NC}"
    
    # Check if get_vault_secret is used in codebase
    VAULT_USAGE=$(grep -r "get_vault_secret\|from.*vault import" "$PROJECT_ROOT/backend/src/" --include="*.py" 2>/dev/null | grep -v ".pyc" | grep -v "test_" | wc -l || echo 0)
    if [ "$VAULT_USAGE" -gt 0 ]; then
        echo -e "${GREEN}✅ Vault functions used in codebase (${VAULT_USAGE} references)${NC}"
    else
        echo -e "${YELLOW}⚠️  INFO: Vault integration exists but not yet used${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  INFO: Vault integration not found (using .env for secrets)${NC}"
fi

echo ""

# ============================================================================
# 4. CHECK HTTPS ENFORCEMENT
# ============================================================================
echo -e "${YELLOW}[4/7] Checking HTTPS enforcement...${NC}"

if [ -f "$PROJECT_ROOT/backend/src/middleware/https_redirect.py" ]; then
    echo -e "${GREEN}✅ HTTPS redirect middleware exists${NC}"
    
    # Check if middleware is registered in main.py
    if grep -q "HTTPSRedirectMiddleware\|add_https_middleware" "$PROJECT_ROOT/backend/src/main.py" 2>/dev/null; then
        echo -e "${GREEN}✅ HTTPS middleware registered in main.py${NC}"
    else
        echo -e "${YELLOW}⚠️  INFO: HTTPS middleware exists but not registered (add to main.py)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  INFO: HTTPS redirect middleware not found${NC}"
fi

# Check for security headers
if grep -q "Strict-Transport-Security\|X-Content-Type-Options\|X-Frame-Options" "$PROJECT_ROOT/backend/src/main.py" "$PROJECT_ROOT/backend/src/middleware/"* 2>/dev/null; then
    echo -e "${GREEN}✅ Security headers configured${NC}"
else
    echo -e "${YELLOW}⚠️  INFO: Security headers may not be configured${NC}"
fi

echo ""

# ============================================================================
# 5. CHECK FOR AMERICAN MEDICAL TERMINOLOGY (COMPLIANCE)
# ============================================================================
echo -e "${YELLOW}[5/7] Checking for American medical terminology...${NC}"

# Look for American drug names (exclude test and validator files)
AMERICAN_DRUG_FOUND=$(grep -r -i "acetaminophen\|albuterol\|epinephrine" "$PROJECT_ROOT/backend/src/" "$PROJECT_ROOT/frontend/src/" --include="*.py" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "test_" | grep -v "validator" | grep -v "#" | grep -v "//" | wc -l || echo 0)

if [ "$AMERICAN_DRUG_FOUND" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  INFO: American medical terminology found (verify if in validators only):${NC}"
    grep -r -i "acetaminophen\|albuterol\|epinephrine" "$PROJECT_ROOT/backend/src/" "$PROJECT_ROOT/frontend/src/" --include="*.py" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "test_" | grep -v "validator" | grep -v "#" | grep -v "//" | head -3 || echo "  (All in test/validator files)"
    echo -e "${YELLOW}   Correct Australian terms: paracetamol, salbutamol, adrenaline${NC}"
else
    echo -e "${GREEN}✅ Australian medical terminology used${NC}"
fi

echo ""

# ============================================================================
# 6. CHECK ENCRYPTION STANDARDS
# ============================================================================
echo -e "${YELLOW}[6/7] Verifying encryption implementations...${NC}"

# Check for weak hashing algorithms (exclude comments)
WEAK_HASH_FOUND=$(grep -r "hashlib\.md5\|hashlib\.sha1" "$PROJECT_ROOT/backend/src/" --include="*.py" 2>/dev/null | grep -v "#" | grep -v "test_" | wc -l || echo 0)
if [ "$WEAK_HASH_FOUND" -gt 0 ]; then
    echo -e "${RED}❌ CRITICAL: Weak hashing algorithm (MD5/SHA1) detected${NC}"
    VIOLATIONS=$((VIOLATIONS + 1))
else
    echo -e "${GREEN}✅ No weak hashing algorithms${NC}"
fi

# Check for Argon2 password hashing
ARGON2_FOUND=$(grep -r "argon2\|Argon2" "$PROJECT_ROOT/backend/src/" --include="*.py" 2>/dev/null | wc -l || echo 0)
if [ "$ARGON2_FOUND" -gt 0 ]; then
    echo -e "${GREEN}✅ Argon2 password hashing used${NC}"
else
    echo -e "${YELLOW}⚠️  INFO: Argon2 not detected (may use bcrypt or passlib)${NC}"
fi

# Check for encryption module
if [ -f "$PROJECT_ROOT/backend/src/security/encryption.py" ]; then
    echo -e "${GREEN}✅ Encryption module exists${NC}"
else
    echo -e "${YELLOW}⚠️  INFO: Encryption module not found${NC}"
fi

echo ""

# ============================================================================
# 7. CHECK AUDIT LOGGING
# ============================================================================
echo -e "${YELLOW}[7/7] Checking audit logging implementation...${NC}"

if [ -f "$PROJECT_ROOT/backend/src/security/events.py" ]; then
    echo -e "${GREEN}✅ Security events module exists${NC}"
else
    echo -e "${YELLOW}⚠️  INFO: Security events module not found${NC}"
fi

# Check for audit log usage in authentication
AUTH_AUDIT=$(grep -r "log_security_event\|audit_log" "$PROJECT_ROOT/backend/src/auth/" --include="*.py" 2>/dev/null | wc -l || echo 0)
if [ "$AUTH_AUDIT" -gt 0 ]; then
    echo -e "${GREEN}✅ Audit logging used in authentication (${AUTH_AUDIT} references)${NC}"
else
    echo -e "${YELLOW}⚠️  INFO: Audit logging may not be comprehensive${NC}"
fi

echo ""

# ============================================================================
# FINAL VERDICT
# ============================================================================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ $VIOLATIONS -eq 0 ]; then
    echo -e "${GREEN}✅ SECURITY AUDIT PASSED - Zero critical violations detected${NC}"
    echo -e "${GREEN}   Safe to commit${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}❌ SECURITY AUDIT FAILED - ${VIOLATIONS} critical violation(s) detected${NC}"
    echo ""
    echo -e "${YELLOW}CRITICAL VIOLATIONS:${NC}"
    echo "  - Hardcoded credentials, API keys, or secrets"
    echo "  - PHI (Protected Health Information) leaks"
    echo "  - Weak encryption algorithms"
    echo ""
    echo -e "${YELLOW}FIX REQUIRED:${NC}"
    echo "  1. Remove all hardcoded credentials → Use Vault or .env"
    echo "  2. Sanitize all PHI before logging → Use anonymization"
    echo "  3. Replace weak algorithms → Use Argon2, SHA-256+"
    echo ""
    echo -e "${YELLOW}DOCUMENTATION:${NC}"
    echo "  - docs/VAULT_INTEGRATION.md"
    echo "  - docs/SECURITY_COMPLIANCE_CHECKLIST.md"
    echo "  - constraints/3-security.md"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi
