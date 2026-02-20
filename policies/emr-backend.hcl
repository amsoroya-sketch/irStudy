# EMR Backend Service Policy
# Grants read access to EMR-specific secrets, database credentials, and shared JWT secret

# Read access to EMR secrets
path "secret/data/emr/*" {
  capabilities = ["read"]
}

# Read access to database secrets
path "secret/data/database/*" {
  capabilities = ["read"]
}

# Read access to shared JWT secret
path "secret/data/shared/jwt-secret" {
  capabilities = ["read"]
}

# Read access to shared API rate limit secret
path "secret/data/shared/api-rate-limit-secret" {
  capabilities = ["read"]
}
