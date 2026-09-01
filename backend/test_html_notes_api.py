#!/usr/bin/env python3
"""
Test HTML OSCE Notes API Endpoints

Tests:
1. List all HTML notes
2. Get single note metadata
3. Get notes by specialty
4. Get specialties list
5. Get HTML content

Usage:
    python test_html_notes_api.py
"""

import requests
import json
from pprint import pprint

BASE_URL = "http://localhost:8001/api/v1"

def test_auth():
    """Get auth token for testing"""
    # Try to login with test user (if exists) or register
    login_data = {
        "username": "test@example.com",
        "password": "TestPassword123!"
    }

    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)

    if response.status_code == 200:
        token = response.json()["access_token"]
        return token

    # If login failed, try to register
    register_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "role": "student"
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)

    if response.status_code in [200, 201]:
        # Try login again
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            return token

    return None


def test_list_html_notes(token):
    """Test 1: List all HTML notes"""
    print("\n" + "="*70)
    print("TEST 1: List all HTML notes (limit 5)")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/html-notes?limit=5", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        notes = response.json()
        print(f"Found {len(notes)} notes:")
        for note in notes:
            print(f"  - {note['note_id']}: {note['title'][:60]}...")
            print(f"    Specialty: {note['specialty']}, Category: {note['category']}")
        return notes[0]['note_id'] if notes else None
    else:
        print(f"Error: {response.text}")
        return None


def test_get_single_note(token, note_id):
    """Test 2: Get single note metadata"""
    print("\n" + "="*70)
    print(f"TEST 2: Get single note metadata ({note_id})")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/html-notes/{note_id}", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        note = response.json()
        print(f"Title: {note['title']}")
        print(f"Specialty: {note['specialty']}")
        print(f"Category: {note['category']}")
        print(f"File size: {note['file_size_kb']} KB")
        print(f"Reading time: {note['estimated_reading_minutes']} minutes")
        print(f"Topics: {note.get('topics', [])}")
        return note['specialty']
    else:
        print(f"Error: {response.text}")
        return None


def test_get_notes_by_specialty(token, specialty):
    """Test 3: Get notes by specialty"""
    print("\n" + "="*70)
    print(f"TEST 3: Get notes by specialty ({specialty})")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/html-notes/by-specialty/{specialty}", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        notes = response.json()
        print(f"Found {len(notes)} notes for {specialty}:")
        for note in notes[:3]:  # Show first 3
            print(f"  - {note['note_id']}: {note['title'][:60]}...")
    else:
        print(f"Error: {response.text}")


def test_get_specialties_list(token):
    """Test 4: Get specialties list"""
    print("\n" + "="*70)
    print("TEST 4: Get specialties list")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/html-notes/specialties/list", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        specialties = response.json()
        print(f"Found {len(specialties)} specialties:")
        for spec in specialties:
            print(f"  - {spec['specialty']}: {spec['count']} notes")
    else:
        print(f"Error: {response.text}")


def test_get_html_content(token, note_id):
    """Test 5: Get HTML content"""
    print("\n" + "="*70)
    print(f"TEST 5: Get HTML content ({note_id})")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/html-notes/{note_id}/content", headers=headers)

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        html_content = response.text
        print(f"Received HTML content ({len(html_content)} bytes)")
        print(f"First 200 characters:")
        print(html_content[:200])
    else:
        print(f"Error: {response.text}")


def main():
    print("🧪 Testing HTML OSCE Notes API Endpoints")
    print("="*70)

    # Get auth token
    print("\n🔐 Authenticating...")
    token = test_auth()

    if not token:
        print("❌ Authentication failed")
        return

    print("✅ Authentication successful")

    # Run tests
    note_id = test_list_html_notes(token)

    if note_id:
        specialty = test_get_single_note(token, note_id)

        if specialty:
            test_get_notes_by_specialty(token, specialty)

        test_get_specialties_list(token)
        test_get_html_content(token, note_id)

    print("\n" + "="*70)
    print("✅ All tests completed")
    print("="*70)


if __name__ == "__main__":
    main()
