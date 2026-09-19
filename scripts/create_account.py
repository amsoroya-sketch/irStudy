#!/usr/bin/env python3
"""Create (or re-verify) a single irStudy account with a chosen role.

Why this exists: POST /api/v1/auth/register creates users with is_verified=False,
get_current_active_user blocks unverified users, and the verification-email
sender is still a TODO. So self-registered accounts are locked out of the app.
This script seeds a ready-to-use, verified account (or fixes an existing one).

Usage:
  # DB is bound to 127.0.0.1:5433 by docker-compose.yml
  export DATABASE_URL="postgresql://postgres:$(cat secrets/db_password.txt)@localhost:5433/irstudy_medical"
  python scripts/create_account.py --email student@example.com \
      --password 'Str0ng!Passphrase' --name "Student Name" --role student

Roles: student | educator | admin
"""
import argparse
import os
import sys
from pathlib import Path

# Reach the backend package (mirrors scripts/create_test_users.py)
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from src.db.models import User, UserRole  # noqa: E402
from src.auth.security import hash_password  # noqa: E402

ROLES = {
    "student": UserRole.STUDENT,
    "educator": UserRole.EDUCATOR,
    "admin": UserRole.ADMIN,
}


def main() -> None:
    ap = argparse.ArgumentParser(description="Create/verify an irStudy account.")
    ap.add_argument("--email", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--role", choices=list(ROLES), default="student")
    args = ap.parse_args()

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        sys.exit(
            "ERROR: set DATABASE_URL, e.g.\n"
            '  export DATABASE_URL="postgresql://postgres:$(cat secrets/db_password.txt)'
            '@localhost:5433/irstudy_medical"'
        )

    engine = create_engine(db_url)
    with Session(engine) as session:
        user = session.query(User).filter(User.email == args.email).first()
        if user:
            user.is_active = True
            user.is_verified = True
            user.role = ROLES[args.role]
            user.password_hash = hash_password(args.password)
            action = "updated (verified + password reset)"
        else:
            user = User(
                email=args.email,
                password_hash=hash_password(args.password),
                full_name=args.name,
                role=ROLES[args.role],
                is_active=True,
                is_verified=True,
            )
            session.add(user)
            action = "created"
        session.commit()
        print(f"✅ Account {action}: {args.email} (role={args.role})")


if __name__ == "__main__":
    main()
