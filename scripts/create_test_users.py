#!/usr/bin/env python3
"""
Create test users for E2E Playwright tests.

This script creates the test users defined in testing/playwright/utils/test-data/users.ts
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import User, UserRole
from src.db.base import Base
from src.auth.security import hash_password
import os

def create_test_users():
    """Create test users matching Playwright test data."""

    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("   Set it in .env or export it:")
        print("   export DATABASE_URL='postgresql://user:pass@localhost:5432/irstudy'")
        sys.exit(1)

    engine = create_engine(db_url)

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    session = Session(engine)

    # Test users from testing/playwright/utils/test-data/users.ts
    test_users = [
        {
            "email": "student@test.com",
            "password": "Student123!@#",
            "full_name": "John Student",
            "role": UserRole.STUDENT,
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "educator@test.com",
            "password": "Educator123!@#",
            "full_name": "Jane Educator",
            "role": UserRole.EDUCATOR,
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "admin@test.com",
            "password": "Admin123!@#",
            "full_name": "Alice Admin",
            "role": UserRole.ADMIN,
            "is_active": True,
            "is_verified": True,
        },
        {
            "email": "inactive@test.com",
            "password": "Inactive123!@#",
            "full_name": "Bob Inactive",
            "role": UserRole.STUDENT,
            "is_active": False,
            "is_verified": True,
        },
        {
            "email": "unverified@test.com",
            "password": "Unverified123!@#",
            "full_name": "Charlie Unverified",
            "role": UserRole.STUDENT,
            "is_active": True,
            "is_verified": False,
        },
    ]

    created_count = 0
    updated_count = 0

    print("=" * 70)
    print("Creating Test Users for E2E Tests")
    print("=" * 70)
    print()

    for user_data in test_users:
        email = user_data["email"]

        # Check if user already exists
        existing_user = session.query(User).filter(User.email == email).first()

        if existing_user:
            # Update existing user
            existing_user.password_hash = hash_password(user_data["password"])
            existing_user.full_name = user_data["full_name"]
            existing_user.role = user_data["role"]
            existing_user.is_active = user_data["is_active"]
            existing_user.is_verified = user_data["is_verified"]
            updated_count += 1
            print(f"✓ Updated: {email} ({user_data['role'].value})")
        else:
            # Create new user
            new_user = User(
                email=email,
                password_hash=hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=user_data["is_active"],
                is_verified=user_data["is_verified"],
            )
            session.add(new_user)
            created_count += 1
            print(f"✓ Created: {email} ({user_data['role'].value})")

    # Commit changes
    try:
        session.commit()
        print()
        print("=" * 70)
        print("✅ SUCCESS")
        print("=" * 70)
        print(f"Created: {created_count} users")
        print(f"Updated: {updated_count} users")
        print(f"Total:   {created_count + updated_count} users")
        print()
        print("Test users are ready for Playwright E2E tests!")
        print()
    except Exception as e:
        session.rollback()
        print()
        print("=" * 70)
        print("❌ ERROR")
        print("=" * 70)
        print(f"Failed to create test users: {e}")
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    create_test_users()
