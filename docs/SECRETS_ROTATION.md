# irStudy Secrets Rotation Guide

**Version**: 1.0.0
**Last Updated**: 2026-02-02

## 1. Rotation Schedule

Quarterly rotation every 90 days for all production secrets.

## 2. Secrets Location

Location: /home/dev/Development/irStudy/secrets/

Secrets to rotate:
- db_password.txt
- redis_password.txt
- neo4j_auth.txt
- anthropic_api_key.txt
- openai_api_key.txt
- qdrant_api_key.txt
- flower_auth.txt
- grafana_password.txt

## 3. PostgreSQL Password Rotation

Generate new password: openssl rand -base64 32
Update database: ALTER USER postgres WITH PASSWORD
Update file: echo new_password into secrets/db_password.txt
Restart: docker-compose restart postgres
Verify: Test connection from backend
Log: Add entry to ROTATION_AUDIT.log

## 4. Redis Password Rotation

Generate new password: openssl rand -base64 32
Update Redis: CONFIG SET requirepass
Update file: secrets/redis_password.txt
Restart: docker-compose restart redis
Verify: Test with redis-cli
Log: Update ROTATION_AUDIT.log

## 5. Neo4j Authentication Rotation

Generate password: openssl rand -base64 32
Update Neo4j: ALTER USER neo4j SET PASSWORD
Update file: Format neo4j:password in secrets/neo4j_auth.txt
Restart: docker-compose restart neo4j
Verify: Test Cypher shell connection
Log: Update ROTATION_AUDIT.log

## 6. Anthropic API Key Rotation

Manual process:
1. Go to https://console.anthropic.com/account/keys
2. Delete old key
3. Create new key
4. Copy to secrets/anthropic_api_key.txt
Restart: docker-compose restart backend
Verify: Test API call
Log: Update ROTATION_AUDIT.log

## 7. OpenAI API Key Rotation

Manual process:
1. Go to https://platform.openai.com/account/api-keys
2. Delete old key
3. Create new key
4. Copy to secrets/openai_api_key.txt
Restart: docker-compose restart backend
Verify: Test API call
Log: Update ROTATION_AUDIT.log

## 8. Emergency Rotation

Immediately upon compromise:
1. Revoke API keys in Anthropic and OpenAI consoles
2. Rotate all database passwords
3. docker-compose down && docker-compose up -d
4. Verify all services healthy
5. Log incident in ROTATION_AUDIT.log

## 9. Scheduled Rotation with Cron

Add to /etc/cron.d/irstudy-rotation:
0 2 1 1,4,7,10 * bash /home/dev/Development/irStudy/docs/rotate_all_secrets.sh

Runs quarterly at 2 AM on first day of each quarter.

## 10. Best Practices

- Automate quarterly rotations
- Alert if secret >90 days old
- Test new secret before removing old
- Keep audit log updated
- Encrypt secrets directory
- Restrict access to authorized users
- Maintain encrypted backup

## References

- HIPAA Security Rule: 45 CFR 164.312(a)(2)(i)
- NIST Password Guidelines: https://csrc.nist.gov/publications/detail/sp/800-132/final
- Docker Secrets: https://docs.docker.com/engine/swarm/secrets/

**Status**: APPROVED FOR PRODUCTION
**Last Review**: 2026-02-02
