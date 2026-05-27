"""
Integration Test: API Performance

Tests API response times under various loads.

PRD: PRD-MVP-004-INTEGRATION-TESTING.md
Target: p95 < 200ms for all endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import time
import statistics

@pytest.mark.integration
@pytest.mark.performance
class TestAPIPerformance:
    """Test API endpoint performance"""

    def test_perf_01_dashboard_overview_response_time(
        self, client: TestClient, auth_headers: dict, user_with_activity
    ):
        """
        Test 8: Dashboard overview performance

        Runs 100 requests and measures response times.

        Target:
        - p50 < 50ms
        - p95 < 150ms
        - p99 < 200ms
        """
        response_times = []

        for _ in range(100):
            start = time.time()
            response = client.get(
                "/api/v1/dashboard/overview",
                headers=auth_headers
            )
            elapsed = (time.time() - start) * 1000  # Convert to ms

            assert response.status_code == 200
            response_times.append(elapsed)

        # Calculate percentiles
        p50 = statistics.median(response_times)
        p95 = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        p99 = statistics.quantiles(response_times, n=100)[98]  # 99th percentile

        print(f"\nDashboard Performance:")
        print(f"  p50: {p50:.2f}ms")
        print(f"  p95: {p95:.2f}ms")
        print(f"  p99: {p99:.2f}ms")

        assert p50 < 50, f"p50 ({p50:.2f}ms) exceeds 50ms target"
        assert p95 < 150, f"p95 ({p95:.2f}ms) exceeds 150ms target"
        assert p99 < 200, f"p99 ({p99:.2f}ms) exceeds 200ms target"

    def test_perf_02_mcq_list_pagination_performance(
        self, client: TestClient, auth_headers: dict, db: Session
    ):
        """
        Test 9: MCQ list pagination performance

        Tests pagination with different page sizes.

        Target: < 100ms for limit=20 (p95)
        """
        from src.db.models import MCQ, MedicalSpecialty, DifficultyLevel

        # Setup: Ensure we have ≥100 MCQs
        existing_count = db.query(MCQ).count()
        if existing_count < 100:
            for i in range(100 - existing_count):
                mcq = MCQ(
                    question_id=f"PERF-TEST-MCQ-{i}",
                    question_text=f"Performance test question {i}",
                    options={"A": "A", "B": "B", "C": "C", "D": "D"},
                    correct_answer="A",
                    explanation="Test",
                    citation="Test",
                    specialty=MedicalSpecialty.GENERAL_PRACTICE,
                    difficulty=DifficultyLevel.MEDIUM,
                    is_published=True
                )
                db.add(mcq)
            db.commit()

        response_times = []

        for _ in range(50):
            start = time.time()
            response = client.get(
                "/api/v1/mcqs",
                params={"limit": 20, "offset": 0},
                headers=auth_headers
            )
            elapsed = (time.time() - start) * 1000

            assert response.status_code == 200
            response_times.append(elapsed)

        p95 = statistics.quantiles(response_times, n=20)[18]

        print(f"\nMCQ List Performance (limit=20):")
        print(f"  p95: {p95:.2f}ms")

        assert p95 < 100, f"p95 ({p95:.2f}ms) exceeds 100ms target"

    def test_perf_03_concurrent_users_simulation(
        self, client: TestClient, db: Session
    ):
        """
        Test 10: Concurrent users (simplified)

        Simulates 10 users rapidly accessing dashboard in sequence.
        (Note: True concurrent load testing requires Locust - see test plan)

        Target: All requests succeed, avg response < 500ms
        """
        from src.db.models import User
        from src.auth.security import hash_password, create_access_token

        # Setup: Create 10 test users and pre-build their auth headers
        user_headers = []
        for i in range(10):
            user = User(
                email=f"concurrent.test.{i}@medical.edu.au",
                password_hash=hash_password("TestPass123!"),
                full_name=f"Concurrent User {i}",
                is_verified=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            token = create_access_token(
                data={"sub": user.email, "user_id": str(user.id)}
            )
            headers = {"Authorization": f"Bearer {token}"}
            user_headers.append(headers)

        # Execute rapid sequential requests (avoids SQLite thread-safety issues)
        results = []
        for headers in user_headers:
            start = time.time()
            response = client.get("/api/v1/dashboard/overview", headers=headers)
            elapsed = (time.time() - start) * 1000

            results.append({
                "status": response.status_code,
                "elapsed_ms": elapsed,
                "success": response.status_code == 200
            })

        # Analyze results
        success_count = sum(1 for r in results if r["success"])
        avg_time = statistics.mean([r["elapsed_ms"] for r in results])

        print(f"\nConcurrent Users Test:")
        print(f"  Success rate: {success_count}/10")
        print(f"  Avg response: {avg_time:.2f}ms")

        assert success_count == 10, f"Only {success_count}/10 requests succeeded"
        assert avg_time < 500, f"Avg response ({avg_time:.2f}ms) exceeds 500ms"
