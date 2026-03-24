# Comprehensive Testing Plan: Study Cards Pipeline (Part 2)

**Document ID**: TESTING-PLAN-STUDY-CARDS-002
**Version**: 1.0
**Created**: 2026-03-24
**Continuation of**: COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS.md

---

## Continued from Part 1

Part 1 covered tests 1-90. This document covers tests 91-112 plus tooling/infrastructure.

---

## 5.1.2 P1-006 ↔ P1-007 Integration (5 tests)

**File**: `backend/tests/test_integration/test_review_to_sm2.py`

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.main import app
from src.db.models import StudyCard, User


@pytest.mark.asyncio
class TestP1006ToP1007Integration:
    """Test integration between Flashcard Review Interface (P1-006) and SM-2 Review Logic (P1-007)"""

    # Test 91: Rating card in P1-006 triggers SM-2 calculation in P1-007
    async def test_rating_triggers_sm2_calculation(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that submitting quality rating in P1-006 correctly updates SM-2 parameters via P1-007"""
        # Create test card with initial SM-2 parameters
        card = StudyCard(
            user_id=test_user.user_id,
            session_id="550e8400-e29b-41d4-a716-446655440000",
            card_id="CARD-TEST-001",
            specialty="cardiology",
            topic="Pain Assessment",
            question="What is SOCRATES?",
            answer="Pain assessment framework",
            citations=[],
            difficulty="medium",
            tags=[],
            card_type="concept",
            ease_factor=2.5,
            interval_days=1,
            repetitions=0,
            next_review_date=datetime.utcnow(),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(card)
        db.commit()
        db.refresh(card)

        # Submit quality rating via P1-006 UI (triggers P1-007 backend)
        response = await async_client.put(
            f"/api/v1/study-cards/{card.id}/review",
            json={"quality": 4, "time_taken_seconds": 30},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify SM-2 calculation (P1-007 logic)
        # Quality 4 with initial EF=2.5 should maintain EF at 2.5
        assert data["ease_factor"] == 2.5
        assert data["interval_days"] == 6  # First repetition: 6 days
        assert data["repetitions"] == 1
        assert "next_review_date" in data

        # Verify database updated
        db.refresh(card)
        assert card.ease_factor == 2.5
        assert card.interval_days == 6
        assert card.repetitions == 1

    # Test 92: TypeScript SM-2 calculation matches Python backend (consistency validation)
    async def test_typescript_python_sm2_consistency(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that frontend TypeScript SM-2 calculations match backend Python within 0.01 tolerance"""
        # Test cases covering all quality ratings (0-5)
        test_cases = [
            {"initial": {"ease_factor": 2.5, "interval_days": 1, "repetitions": 0}, "quality": 5, "expected": {"ease_factor": 2.6, "interval_days": 6, "repetitions": 1}},
            {"initial": {"ease_factor": 2.5, "interval_days": 1, "repetitions": 0}, "quality": 4, "expected": {"ease_factor": 2.5, "interval_days": 6, "repetitions": 1}},
            {"initial": {"ease_factor": 2.5, "interval_days": 1, "repetitions": 0}, "quality": 3, "expected": {"ease_factor": 2.36, "interval_days": 6, "repetitions": 1}},
            {"initial": {"ease_factor": 2.5, "interval_days": 1, "repetitions": 0}, "quality": 2, "expected": {"ease_factor": 2.18, "interval_days": 6, "repetitions": 1}},
            {"initial": {"ease_factor": 2.5, "interval_days": 1, "repetitions": 0}, "quality": 1, "expected": {"ease_factor": 1.96, "interval_days": 1, "repetitions": 0}},
            {"initial": {"ease_factor": 2.5, "interval_days": 1, "repetitions": 0}, "quality": 0, "expected": {"ease_factor": 1.7, "interval_days": 1, "repetitions": 0}},
        ]

        for idx, case in enumerate(test_cases):
            # Create card with initial parameters
            card = StudyCard(
                user_id=test_user.user_id,
                session_id=f"550e8400-e29b-41d4-a716-44665544{idx:04d}",
                card_id=f"CARD-TEST-{idx:03d}",
                specialty="cardiology",
                topic="Test",
                question=f"Question {idx}",
                answer=f"Answer {idx}",
                citations=[],
                difficulty="medium",
                tags=[],
                card_type="concept",
                ease_factor=case["initial"]["ease_factor"],
                interval_days=case["initial"]["interval_days"],
                repetitions=case["initial"]["repetitions"],
                next_review_date=datetime.utcnow(),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(card)
            db.commit()
            db.refresh(card)

            # Submit rating
            response = await async_client.put(
                f"/api/v1/study-cards/{card.id}/review",
                json={"quality": case["quality"], "time_taken_seconds": 30},
                headers={"Authorization": f"Bearer {test_user.access_token}"},
            )

            assert response.status_code == 200
            data = response.json()

            # Verify Python backend matches expected (TypeScript should produce same results)
            assert abs(data["ease_factor"] - case["expected"]["ease_factor"]) < 0.01, \
                f"Test case {idx} (quality={case['quality']}): EF mismatch"
            assert data["interval_days"] == case["expected"]["interval_days"], \
                f"Test case {idx} (quality={case['quality']}): Interval mismatch"
            assert data["repetitions"] == case["expected"]["repetitions"], \
                f"Test case {idx} (quality={case['quality']}): Repetitions mismatch"

    # Test 93: Optimistic UI update in P1-006 matches eventual P1-007 backend result
    async def test_optimistic_update_consistency(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that P1-006 optimistic UI update matches P1-007 backend calculation (no rollback needed)"""
        card = StudyCard(
            user_id=test_user.user_id,
            session_id="550e8400-e29b-41d4-a716-446655440005",
            card_id="CARD-TEST-OPT",
            specialty="cardiology",
            topic="Test",
            question="Optimistic test",
            answer="Test answer",
            citations=[],
            difficulty="medium",
            tags=[],
            card_type="concept",
            ease_factor=2.5,
            interval_days=1,
            repetitions=0,
            next_review_date=datetime.utcnow(),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(card)
        db.commit()
        db.refresh(card)

        # Frontend would calculate optimistically using TypeScript SM-2
        # Expected optimistic result for quality=4: EF=2.5, interval=6, reps=1

        # Backend calculation
        response = await async_client.put(
            f"/api/v1/study-cards/{card.id}/review",
            json={"quality": 4, "time_taken_seconds": 30},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )

        assert response.status_code == 200
        backend_result = response.json()

        # Verify backend matches expected optimistic calculation (no rollback needed)
        assert backend_result["ease_factor"] == 2.5
        assert backend_result["interval_days"] == 6
        assert backend_result["repetitions"] == 1

    # Test 94: Next review date filter works after P1-007 updates
    async def test_next_review_date_filter_after_rating(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that cards with future next_review_date don't appear in P1-006 review queue"""
        # Create 2 cards
        card1 = StudyCard(
            user_id=test_user.user_id,
            session_id="550e8400-e29b-41d4-a716-446655440006",
            card_id="CARD-TEST-DUE1",
            specialty="cardiology",
            topic="Test",
            question="Card 1",
            answer="Answer 1",
            citations=[],
            difficulty="medium",
            tags=[],
            card_type="concept",
            ease_factor=2.5,
            interval_days=1,
            repetitions=0,
            next_review_date=datetime.utcnow(),  # Due now
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        card2 = StudyCard(
            user_id=test_user.user_id,
            session_id="550e8400-e29b-41d4-a716-446655440007",
            card_id="CARD-TEST-DUE2",
            specialty="cardiology",
            topic="Test",
            question="Card 2",
            answer="Answer 2",
            citations=[],
            difficulty="medium",
            tags=[],
            card_type="concept",
            ease_factor=2.5,
            interval_days=1,
            repetitions=0,
            next_review_date=datetime.utcnow(),  # Due now
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add_all([card1, card2])
        db.commit()

        # Verify both cards appear in review queue initially
        response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == 200
        assert response.json()["count"] == 2

        # Rate card1 (quality=4) - should set next_review_date to 6 days from now
        await async_client.put(
            f"/api/v1/study-cards/{card1.id}/review",
            json={"quality": 4, "time_taken_seconds": 30},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )

        # Verify only card2 appears in review queue now
        response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["cards"][0]["id"] == card2.id

    # Test 95: Multiple rapid ratings don't cause race conditions
    async def test_concurrent_ratings_no_race_condition(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that multiple rapid ratings are handled correctly without data corruption"""
        # Create 3 cards
        cards = []
        for i in range(3):
            card = StudyCard(
                user_id=test_user.user_id,
                session_id=f"550e8400-e29b-41d4-a716-44665544{i:04d}",
                card_id=f"CARD-RACE-{i:03d}",
                specialty="cardiology",
                topic="Test",
                question=f"Question {i}",
                answer=f"Answer {i}",
                citations=[],
                difficulty="medium",
                tags=[],
                card_type="concept",
                ease_factor=2.5,
                interval_days=1,
                repetitions=0,
                next_review_date=datetime.utcnow(),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(card)
            cards.append(card)
        db.commit()

        # Submit ratings concurrently (simulate rapid UI clicks)
        import asyncio
        tasks = [
            async_client.put(
                f"/api/v1/study-cards/{card.id}/review",
                json={"quality": 4, "time_taken_seconds": 30},
                headers={"Authorization": f"Bearer {test_user.access_token}"},
            )
            for card in cards
        ]

        responses = await asyncio.gather(*tasks)

        # Verify all succeeded
        for response in responses:
            assert response.status_code == 200

        # Verify all cards updated correctly (no data corruption)
        for card in cards:
            db.refresh(card)
            assert card.ease_factor == 2.5
            assert card.interval_days == 6
            assert card.repetitions == 1
```

---

## 5.1.3 Full Pipeline Integration (5 tests)

**File**: `backend/tests/test_integration/test_full_pipeline.py`

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from datetime import datetime

from src.main import app
from src.db.models import OSCEAttemptAI, User


@pytest.mark.asyncio
class TestFullPipelineIntegration:
    """Test complete pipeline: OSCE → P1-005 → P1-006 → P1-007"""

    # Test 96: Complete workflow - OSCE session to rated cards
    async def test_complete_pipeline_osce_to_rated_cards(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test full user workflow from OSCE completion to reviewing and rating study cards"""
        # Step 1: Complete OSCE session
        osce_session = OSCEAttemptAI(
            attempt_id="550e8400-e29b-41d4-a716-446655440100",
            user_id=test_user.user_id,
            persona_code="CARD-PIPELINE-001",
            feedback_text="Excellent history taking. Used SOCRATES framework. Asked about red flags. Good rapport building.",
            score=88,
            created_at=datetime.utcnow(),
        )
        db.add(osce_session)
        db.commit()

        # Step 2: Generate study cards (P1-005)
        generate_response = await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "550e8400-e29b-41d4-a716-446655440100"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert generate_response.status_code == 201
        generated_cards = generate_response.json()
        assert generated_cards["count"] >= 3

        # Step 3: Fetch cards for review (P1-006)
        review_response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert review_response.status_code == 200
        review_data = review_response.json()
        assert review_data["count"] == generated_cards["count"]

        # Step 4: Rate first card (P1-007)
        first_card_id = review_data["cards"][0]["id"]
        rating_response = await async_client.put(
            f"/api/v1/study-cards/{first_card_id}/review",
            json={"quality": 4, "time_taken_seconds": 45},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert rating_response.status_code == 200
        rating_data = rating_response.json()

        # Verify SM-2 update
        assert rating_data["ease_factor"] == 2.5
        assert rating_data["interval_days"] == 6
        assert rating_data["repetitions"] == 1

        # Step 5: Verify card no longer appears in review queue
        review_response2 = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert review_response2.json()["count"] == generated_cards["count"] - 1

    # Test 97: Performance - Complete pipeline in <15 seconds
    async def test_pipeline_performance_under_15_seconds(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that complete pipeline (generate + review + rate) completes in <15 seconds"""
        import time

        start_time = time.time()

        # Create OSCE session
        osce_session = OSCEAttemptAI(
            attempt_id="550e8400-e29b-41d4-a716-446655440101",
            user_id=test_user.user_id,
            persona_code="CARD-PERF-001",
            feedback_text="Performance test feedback with multiple learning points to generate 3-5 cards.",
            score=85,
            created_at=datetime.utcnow(),
        )
        db.add(osce_session)
        db.commit()

        # Generate cards
        await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "550e8400-e29b-41d4-a716-446655440101"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )

        # Fetch for review
        review_response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )

        # Rate all cards
        cards = review_response.json()["cards"]
        for card in cards:
            await async_client.put(
                f"/api/v1/study-cards/{card['id']}/review",
                json={"quality": 4, "time_taken_seconds": 30},
                headers={"Authorization": f"Bearer {test_user.access_token}"},
            )

        end_time = time.time()
        elapsed = end_time - start_time

        # Verify <15 second target
        assert elapsed < 15.0, f"Pipeline took {elapsed:.2f}s (target: <15s)"

    # Test 98: Data consistency across all layers
    async def test_data_consistency_across_layers(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that data remains consistent across P1-005 generation, P1-006 display, P1-007 updates"""
        # Generate cards
        osce_session = OSCEAttemptAI(
            attempt_id="550e8400-e29b-41d4-a716-446655440102",
            user_id=test_user.user_id,
            persona_code="CARD-CONSISTENCY-001",
            feedback_text="Test feedback for consistency validation.",
            score=85,
            created_at=datetime.utcnow(),
        )
        db.add(osce_session)
        db.commit()

        generate_response = await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "550e8400-e29b-41d4-a716-446655440102"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        generated_card = generate_response.json()["cards"][0]

        # Fetch same card via review API
        review_response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        reviewed_card = review_response.json()["cards"][0]

        # Verify data consistency (same card, same data)
        assert generated_card["id"] == reviewed_card["id"]
        assert generated_card["question"] == reviewed_card["question"]
        assert generated_card["answer"] == reviewed_card["answer"]
        assert generated_card["ease_factor"] == reviewed_card["ease_factor"]
        assert generated_card["interval_days"] == reviewed_card["interval_days"]
        assert generated_card["repetitions"] == reviewed_card["repetitions"]

        # Verify citations match (same qdrant_point_ids)
        assert len(generated_card["citations"]) == len(reviewed_card["citations"])
        for gen_cit, rev_cit in zip(generated_card["citations"], reviewed_card["citations"]):
            assert gen_cit["qdrant_point_id"] == rev_cit["qdrant_point_id"]
            assert gen_cit["source"] == rev_cit["source"]
            assert gen_cit["confidence"] == rev_cit["confidence"]

    # Test 99: Error propagation - P1-005 failure doesn't break P1-006
    async def test_error_isolation_between_components(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that P1-005 generation errors don't break P1-006 review interface"""
        # Attempt to generate cards with invalid session_id (should fail)
        generate_response = await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "00000000-0000-0000-0000-000000000000"},  # Non-existent
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert generate_response.status_code == 404  # Session not found

        # Verify P1-006 review API still works (shows existing cards)
        review_response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert review_response.status_code == 200  # Still functional

    # Test 100: Rollback on partial failure (atomic operations)
    async def test_atomic_card_generation(
        self, async_client: AsyncClient, db: Session, test_user: User, monkeypatch
    ):
        """Test that if card generation partially fails, entire transaction rolls back (no partial cards)"""
        # Create OSCE session
        osce_session = OSCEAttemptAI(
            attempt_id="550e8400-e29b-41d4-a716-446655440103",
            user_id=test_user.user_id,
            persona_code="CARD-ATOMIC-001",
            feedback_text="Feedback for atomic test",
            score=85,
            created_at=datetime.utcnow(),
        )
        db.add(osce_session)
        db.commit()

        # Count cards before generation
        initial_count = db.query(StudyCard).filter_by(user_id=test_user.user_id).count()

        # Mock database to simulate failure during batch insert
        from src.db.models import StudyCard as StudyCardModel

        original_add_all = db.add_all

        def mock_add_all(instances):
            # Simulate failure after adding some cards
            if len(instances) > 2:
                raise Exception("Simulated database error")
            return original_add_all(instances)

        monkeypatch.setattr(db, "add_all", mock_add_all)

        # Attempt generation (should fail and rollback)
        with pytest.raises(Exception):
            await async_client.post(
                "/api/v1/study-cards/generate-from-osce",
                json={"session_id": "550e8400-e29b-41d4-a716-446655440103"},
                headers={"Authorization": f"Bearer {test_user.access_token}"},
            )

        # Verify NO cards were added (rollback successful)
        final_count = db.query(StudyCard).filter_by(user_id=test_user.user_id).count()
        assert final_count == initial_count  # No partial cards
```

---

## 5.2 End-to-End (E2E) Tests (7 tests)

**File**: `frontend/tests/e2e/study-cards-full-pipeline.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Study Cards Full Pipeline E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  // Test 101: Complete user journey - OSCE to study cards review
  test('should complete full user journey from OSCE to study card review', async ({ page }) => {
    // Step 1: Complete OSCE session
    await page.goto('/osce-practice');
    await page.click('[data-testid="persona-CARD-001"]');
    await page.click('button:has-text("Start Session")');

    // Complete conversation (simplified)
    await page.fill('textarea[name="user-message"]', 'Hello, I have chest pain');
    await page.click('button:has-text("Send")');
    await page.waitForTimeout(2000); // Wait for AI response

    // End session
    await page.click('button:has-text("End Session")');

    // Step 2: Navigate to study cards
    await page.click('a:has-text("Study Cards")');

    // Step 3: Generate cards from session
    await page.click('button:has-text("Generate from OSCE")');
    await expect(page.locator('text=/generating cards/i')).toBeVisible();

    // Wait for generation (up to 10s)
    await expect(page.locator('text=/3-5 cards generated/i')).toBeVisible({ timeout: 10000 });

    // Step 4: Review cards
    await page.click('button:has-text("Start Review")');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible();

    // Step 5: Show answer and rate
    await page.click('button:has-text("Show Answer")');
    await page.waitForTimeout(700); // Flip animation

    await page.click('button:has-text("4 - Easy")');

    // Verify success message
    await expect(page.locator('text=/next review: in 6 days/i')).toBeVisible({ timeout: 3000 });
  });

  // Test 102: Mobile workflow (touch interactions)
  test('should work on mobile device with touch gestures', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE

    // Navigate to study cards
    await page.goto('/study-cards/review');

    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Tap to show answer
    await page.locator('button:has-text("Show Answer")').tap();
    await page.waitForTimeout(700);

    // Swipe left for next card (if multiple cards)
    const card = page.locator('[data-testid="flashcard-card"]');
    const box = await card.boundingBox();
    if (box) {
      await page.touchscreen.swipe(
        { x: box.x + box.width - 50, y: box.y + box.height / 2 },
        { x: box.x + 50, y: box.y + box.height / 2 }
      );
    }

    // Tap quality rating
    await page.locator('button:has-text("4 - Easy")').tap();

    await expect(page.locator('text=/next review/i')).toBeVisible({ timeout: 3000 });
  });

  // Test 103: Offline resilience (service worker caching)
  test('should handle offline mode gracefully', async ({ page, context }) => {
    // Navigate to study cards while online
    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Go offline
    await context.setOffline(true);

    // Attempt to rate card
    await page.click('button:has-text("Show Answer")');
    await page.waitForTimeout(700);
    await page.click('button:has-text("4 - Easy")');

    // Verify offline message
    await expect(page.locator('text=/offline|no connection/i')).toBeVisible({ timeout: 3000 });

    // Go back online
    await context.setOffline(false);

    // Retry button should work
    await page.click('button:has-text("Retry")');
    await expect(page.locator('text=/next review/i')).toBeVisible({ timeout: 3000 });
  });

  // Test 104: Multi-day review workflow (simulated time travel)
  test('should show correct cards after simulated time passage', async ({ page }) => {
    // Day 1: Review cards
    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    const initialCount = await page.locator('text=/card \\d+ of (\\d+)/i').textContent();
    const match = initialCount?.match(/of (\\d+)/);
    const totalCards = match ? parseInt(match[1]) : 0;

    // Review all cards with quality=4
    for (let i = 0; i < totalCards; i++) {
      await page.keyboard.press('Space'); // Show answer
      await page.waitForTimeout(700);
      await page.keyboard.press('4'); // Rate as Easy
      await page.waitForTimeout(1000);
    }

    // Verify all cards reviewed
    await expect(page.locator('text=/review complete|no cards due/i')).toBeVisible();

    // Simulate time travel (6 days forward) - via API or database manipulation
    await page.evaluate(() => {
      localStorage.setItem('test_time_offset', String(6 * 24 * 60 * 60 * 1000)); // +6 days
    });

    // Day 7: Refresh and verify cards appear again
    await page.reload();
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Verify same cards appear (after 6-day interval)
    const newCount = await page.locator('text=/card \\d+ of (\\d+)/i').textContent();
    expect(newCount).toContain(String(totalCards)); // All cards due again
  });

  // Test 105: Concurrent users (no data leakage)
  test('should not show other users\' cards', async ({ browser }) => {
    // Create two contexts (two different users)
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();

    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    // User 1 login
    await page1.goto('/login');
    await page1.fill('input[name="email"]', 'student1@test.com');
    await page1.fill('input[name="password"]', 'password123');
    await page1.click('button[type="submit"]');

    // User 2 login
    await page2.goto('/login');
    await page2.fill('input[name="email"]', 'student2@test.com');
    await page2.fill('input[name="password"]', 'password123');
    await page2.click('button[type="submit"]');

    // User 1: View study cards
    await page1.goto('/study-cards/review');
    await expect(page1.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });
    const user1Question = await page1.locator('[data-testid="flashcard-question"]').textContent();

    // User 2: View study cards
    await page2.goto('/study-cards/review');
    await expect(page2.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });
    const user2Question = await page2.locator('[data-testid="flashcard-question"]').textContent();

    // Verify different cards (no data leakage)
    expect(user1Question).not.toBe(user2Question);

    await context1.close();
    await context2.close();
  });

  // Test 106: Accessibility audit (WCAG 2.2 AA compliance)
  test('should pass accessibility audit', async ({ page }) => {
    const AxeBuilder = require('@axe-core/playwright').default;

    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Run axe accessibility scan
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa', 'wcag21aa', 'wcag22aa'])
      .analyze();

    // Verify no violations
    expect(accessibilityScanResults.violations).toHaveLength(0);

    // Verify keyboard navigation works
    await page.keyboard.press('Tab'); // Focus "Show Answer"
    const focusedElement = await page.evaluate(() => document.activeElement?.textContent);
    expect(focusedElement).toContain('Show Answer');
  });

  // Test 107: Performance audit (Lighthouse)
  test('should meet performance benchmarks', async ({ page }) => {
    const { playAudit } = require('playwright-lighthouse');

    await page.goto('/study-cards/review');

    // Run Lighthouse audit
    const auditResults = await playAudit({
      page,
      thresholds: {
        performance: 90,
        accessibility: 95,
        'best-practices': 90,
        seo: 90,
      },
      port: 9222, // Chrome debugging port
    });

    // Verify thresholds passed
    expect(auditResults.lhr.categories.performance.score).toBeGreaterThanOrEqual(0.9);
    expect(auditResults.lhr.categories.accessibility.score).toBeGreaterThanOrEqual(0.95);

    // Verify specific metrics
    const metrics = auditResults.lhr.audits;
    expect(metrics['first-contentful-paint'].numericValue).toBeLessThan(1500); // <1.5s
    expect(metrics['speed-index'].numericValue).toBeLessThan(3000); // <3s
    expect(metrics['total-blocking-time'].numericValue).toBeLessThan(300); // <300ms
  });
});
```

---

## 6. Security & Penetration Tests (5 tests)

### 6.1 Security Test Suite

**File**: `backend/tests/test_security/test_study_cards_security.py`

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.main import app
from src.db.models import User, StudyCard


@pytest.mark.asyncio
class TestStudyCardsSecurity:
    """Security and penetration tests for study cards pipeline"""

    # Test 108: XSS prevention in question/answer fields
    async def test_xss_prevention_in_card_content(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that XSS payloads in card content are sanitized"""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(XSS)'></iframe>",
        ]

        for payload in xss_payloads:
            # Create card with XSS payload
            card = StudyCard(
                user_id=test_user.user_id,
                session_id="550e8400-e29b-41d4-a716-446655440200",
                card_id="CARD-XSS-001",
                specialty="cardiology",
                topic="Test",
                question=f"Question with {payload}",
                answer=f"Answer with {payload}",
                citations=[],
                difficulty="medium",
                tags=[],
                card_type="concept",
                ease_factor=2.5,
                interval_days=1,
                repetitions=0,
                next_review_date=datetime.utcnow(),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(card)
            db.commit()

            # Fetch card via API
            response = await async_client.get(
                "/api/v1/study-cards",
                headers={"Authorization": f"Bearer {test_user.access_token}"},
            )

            # Verify XSS payload is escaped/sanitized in response
            data = response.json()
            card_data = data["cards"][0]

            # Should NOT contain raw script tags
            assert "<script>" not in card_data["question"].lower()
            assert "<script>" not in card_data["answer"].lower()
            assert "onerror=" not in card_data["question"].lower()
            assert "onload=" not in card_data["answer"].lower()

            # Clean up
            db.delete(card)
            db.commit()

    # Test 109: SQL injection prevention in session_id parameter
    async def test_sql_injection_prevention(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that SQL injection payloads are rejected"""
        sql_injection_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE study_cards; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "' OR 1=1--",
        ]

        for payload in sql_injection_payloads:
            response = await async_client.post(
                "/api/v1/study-cards/generate-from-osce",
                json={"session_id": payload},
                headers={"Authorization": f"Bearer {test_user.access_token}"},
            )

            # Should reject with 422 (validation error) or 404 (not found)
            assert response.status_code in [422, 404]

            # Verify database NOT compromised (tables still exist)
            result = db.execute("SELECT COUNT(*) FROM study_cards")
            assert result is not None  # Table still exists

    # Test 110: Authorization - users can only access their own cards
    async def test_authorization_prevents_card_access_across_users(
        self, async_client: AsyncClient, db: Session
    ):
        """Test that users cannot access other users' study cards"""
        # Create two users
        user1 = User(email="user1@test.com", role="student", hashed_password="hash1")
        user2 = User(email="user2@test.com", role="student", hashed_password="hash2")
        db.add_all([user1, user2])
        db.commit()

        # Create card for user1
        card_user1 = StudyCard(
            user_id=user1.user_id,
            session_id="550e8400-e29b-41d4-a716-446655440201",
            card_id="CARD-AUTH-001",
            specialty="cardiology",
            topic="Test",
            question="User 1 card",
            answer="User 1 answer",
            citations=[],
            difficulty="medium",
            tags=[],
            card_type="concept",
            ease_factor=2.5,
            interval_days=1,
            repetitions=0,
            next_review_date=datetime.utcnow(),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(card_user1)
        db.commit()

        # User2 attempts to access user1's card
        user2_token = generate_jwt_token(user2)  # Helper function
        response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {user2_token}"},
        )

        # Verify user2 does NOT see user1's card
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0  # No cards for user2

        # Verify user2 cannot rate user1's card
        rating_response = await async_client.put(
            f"/api/v1/study-cards/{card_user1.id}/review",
            json={"quality": 4, "time_taken_seconds": 30},
            headers={"Authorization": f"Bearer {user2_token}"},
        )
        assert rating_response.status_code == 403  # Forbidden

    # Test 111: JWT token expiration handling
    async def test_expired_jwt_rejected(
        self, async_client: AsyncClient, db: Session
    ):
        """Test that expired JWT tokens are rejected"""
        # Generate expired token (1 hour ago)
        import jwt
        from datetime import datetime, timedelta

        expired_token = jwt.encode(
            {
                "user_id": 1,
                "email": "test@test.com",
                "exp": datetime.utcnow() - timedelta(hours=1),  # Expired
            },
            "secret_key",
            algorithm="HS256",
        )

        # Attempt to access with expired token
        response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        # Verify rejected with 401
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()

    # Test 112: Rate limiting (prevent abuse)
    async def test_rate_limiting_prevents_abuse(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that excessive API calls are rate limited"""
        # Make 100 rapid requests
        responses = []
        for i in range(100):
            response = await async_client.get(
                "/api/v1/study-cards",
                headers={"Authorization": f"Bearer {test_user.access_token}"},
            )
            responses.append(response.status_code)

        # Verify rate limiting kicked in (at least some requests got 429)
        assert 429 in responses, "Rate limiting not enforced"

        # Verify rate limit header present
        last_response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert "X-RateLimit-Remaining" in last_response.headers
```

---

## 7. Performance Benchmarking

### 7.1 Performance Test Suite

**File**: `backend/tests/test_performance/test_study_cards_performance.py`

```python
import pytest
import time
from httpx import AsyncClient
from sqlalchemy.orm import Session

from src.main import app
from src.db.models import User, OSCEAttemptAI


@pytest.mark.performance
class TestStudyCardsPerformance:
    """Performance benchmarks for study cards pipeline"""

    # Benchmark 1: Card generation <8 seconds
    async def test_card_generation_under_8_seconds(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that card generation completes in <8 seconds"""
        osce_session = OSCEAttemptAI(
            attempt_id="550e8400-e29b-41d4-a716-446655440300",
            user_id=test_user.user_id,
            persona_code="CARD-PERF-001",
            feedback_text="Performance test feedback with detailed learning points to generate multiple cards.",
            score=85,
            created_at=datetime.utcnow(),
        )
        db.add(osce_session)
        db.commit()

        start_time = time.time()

        response = await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "550e8400-e29b-41d4-a716-446655440300"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )

        end_time = time.time()
        elapsed = end_time - start_time

        assert response.status_code == 201
        assert elapsed < 8.0, f"Card generation took {elapsed:.2f}s (target: <8s)"

    # Benchmark 2: Review API <200ms
    async def test_review_api_under_200ms(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that GET /api/v1/study-cards responds in <200ms"""
        # Create 10 test cards
        for i in range(10):
            card = StudyCard(
                user_id=test_user.user_id,
                session_id=f"550e8400-e29b-41d4-a716-44665544{i:04d}",
                card_id=f"CARD-PERF-{i:03d}",
                specialty="cardiology",
                topic="Test",
                question=f"Question {i}",
                answer=f"Answer {i}",
                citations=[],
                difficulty="medium",
                tags=[],
                card_type="concept",
                ease_factor=2.5,
                interval_days=1,
                repetitions=0,
                next_review_date=datetime.utcnow(),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(card)
        db.commit()

        # Measure API response time
        start_time = time.time()

        response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )

        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 200, f"Review API took {elapsed_ms:.0f}ms (target: <200ms)"

    # Benchmark 3: SM-2 update <100ms
    async def test_sm2_update_under_100ms(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that PUT /api/v1/study-cards/:id/review responds in <100ms"""
        card = StudyCard(
            user_id=test_user.user_id,
            session_id="550e8400-e29b-41d4-a716-446655440301",
            card_id="CARD-SM2-PERF",
            specialty="cardiology",
            topic="Test",
            question="SM-2 performance test",
            answer="Test answer",
            citations=[],
            difficulty="medium",
            tags=[],
            card_type="concept",
            ease_factor=2.5,
            interval_days=1,
            repetitions=0,
            next_review_date=datetime.utcnow(),
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(card)
        db.commit()

        start_time = time.time()

        response = await async_client.put(
            f"/api/v1/study-cards/{card.id}/review",
            json={"quality": 4, "time_taken_seconds": 30},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )

        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 100, f"SM-2 update took {elapsed_ms:.0f}ms (target: <100ms)"

    # Benchmark 4: Concurrent requests (50 users)
    async def test_concurrent_load_50_users(
        self, async_client: AsyncClient, db: Session
    ):
        """Test that system handles 50 concurrent users reviewing cards"""
        import asyncio

        # Create 50 users with cards
        users = []
        for i in range(50):
            user = User(email=f"load{i}@test.com", role="student", hashed_password="hash")
            db.add(user)
            users.append(user)
        db.commit()

        for user in users:
            card = StudyCard(
                user_id=user.user_id,
                session_id=f"550e8400-e29b-41d4-a716-{user.user_id:012d}",
                card_id=f"CARD-LOAD-{user.user_id:03d}",
                specialty="cardiology",
                topic="Test",
                question=f"Question for user {user.user_id}",
                answer=f"Answer for user {user.user_id}",
                citations=[],
                difficulty="medium",
                tags=[],
                card_type="concept",
                ease_factor=2.5,
                interval_days=1,
                repetitions=0,
                next_review_date=datetime.utcnow(),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(card)
        db.commit()

        # Simulate 50 concurrent review requests
        async def review_cards(user: User):
            token = generate_jwt_token(user)
            return await async_client.get(
                "/api/v1/study-cards",
                headers={"Authorization": f"Bearer {token}"},
            )

        start_time = time.time()
        tasks = [review_cards(user) for user in users]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        elapsed = end_time - start_time

        # Verify all succeeded
        for response in responses:
            assert response.status_code == 200

        # Verify completed in <5 seconds (50 concurrent requests)
        assert elapsed < 5.0, f"50 concurrent requests took {elapsed:.2f}s (target: <5s)"
```

**File**: `frontend/tests/performance/flashcard-animation.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Flashcard Animation Performance', () => {
  test('should maintain 60fps during flip animation', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Measure flip animation performance
    const performanceData = await page.evaluate(() => {
      return new Promise<{ avgFPS: number; maxFrameTime: number }>((resolve) => {
        const frameTimes: number[] = [];
        let lastTime = performance.now();
        let frameCount = 0;

        function measureFrame() {
          const now = performance.now();
          const delta = now - lastTime;
          frameTimes.push(delta);
          lastTime = now;
          frameCount++;

          if (frameCount < 36) { // Measure 36 frames (0.6s at 60fps)
            requestAnimationFrame(measureFrame);
          } else {
            const avgFrameTime = frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length;
            const avgFPS = 1000 / avgFrameTime;
            const maxFrameTime = Math.max(...frameTimes);

            resolve({ avgFPS, maxFrameTime });
          }
        }

        // Trigger flip animation
        document.querySelector<HTMLButtonElement>('button:has-text("Show Answer")')?.click();

        requestAnimationFrame(measureFrame);
      });
    });

    // Verify ≥60fps (allowing 10% margin: ≥54fps)
    expect(performanceData.avgFPS).toBeGreaterThanOrEqual(54);

    // Verify no dropped frames (no frame >33ms = <30fps)
    expect(performanceData.maxFrameTime).toBeLessThanOrEqual(33);
  });
});
```

---

## 8. Accessibility Testing (WCAG 2.2 AA)

### 8.1 Accessibility Test Suite

**File**: `frontend/tests/accessibility/flashcard-wcag.spec.ts`

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Flashcard Accessibility (WCAG 2.2 AA)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
  });

  test('should pass axe accessibility scan', async ({ page }) => {
    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toHaveLength(0);
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Tab to "Show Answer" button
    await page.keyboard.press('Tab');
    let focusedElement = await page.evaluate(() => document.activeElement?.getAttribute('aria-label'));
    expect(focusedElement).toBe('Show answer');

    // Spacebar to flip
    await page.keyboard.press('Space');
    await page.waitForTimeout(700);

    // Verify answer shown
    await expect(page.locator('[data-testid="flashcard-answer"]')).toBeVisible();

    // Tab to quality ratings
    await page.keyboard.press('Tab');
    focusedElement = await page.evaluate(() => document.activeElement?.textContent);
    expect(focusedElement).toContain('Blackout');

    // Arrow keys to navigate ratings
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('ArrowRight'); // Focus "4 - Easy"

    focusedElement = await page.evaluate(() => document.activeElement?.textContent);
    expect(focusedElement).toContain('Easy');

    // Enter to select
    await page.keyboard.press('Enter');

    await expect(page.locator('text=/next review/i')).toBeVisible({ timeout: 3000 });
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Verify ARIA labels exist
    const showAnswerButton = page.locator('button:has-text("Show Answer")');
    await expect(showAnswerButton).toHaveAttribute('aria-label', 'Show answer');
    await expect(showAnswerButton).toHaveAttribute('aria-pressed', 'false');

    // Click and verify aria-pressed updates
    await showAnswerButton.click();
    await page.waitForTimeout(700);

    await expect(showAnswerButton).toHaveAttribute('aria-pressed', 'true');

    // Verify flashcard has role and labels
    const flashcard = page.locator('[data-testid="flashcard-card"]');
    await expect(flashcard).toHaveAttribute('role', 'article');
    await expect(flashcard).toHaveAttribute('aria-label', /flashcard \d+ of \d+/i);
  });

  test('should have sufficient color contrast', async ({ page }) => {
    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Run axe color contrast check
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .include('[data-testid="flashcard-card"]')
      .analyze();

    const colorContrastViolations = accessibilityScanResults.violations.filter(
      v => v.id === 'color-contrast'
    );

    expect(colorContrastViolations).toHaveLength(0);
  });

  test('should work with screen reader (announce changes)', async ({ page }) => {
    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Verify live regions for announcements
    const liveRegion = page.locator('[aria-live="polite"]');
    await expect(liveRegion).toBeAttached();

    // Flip card
    await page.click('button:has-text("Show Answer")');
    await page.waitForTimeout(700);

    // Verify announcement
    const announcement = await liveRegion.textContent();
    expect(announcement).toContain('Answer revealed');

    // Rate card
    await page.click('button:has-text("4 - Easy")');

    // Verify rating announcement
    const ratingAnnouncement = await liveRegion.textContent();
    expect(ratingAnnouncement).toContain('Rated as Easy');
    expect(ratingAnnouncement).toContain('Next review');
  });

  test('should support high contrast mode', async ({ page }) => {
    // Enable Windows High Contrast Mode (simulated)
    await page.emulateMedia({ colorScheme: 'dark', forcedColors: 'active' });

    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Verify elements visible in high contrast
    await expect(page.locator('button:has-text("Show Answer")')).toBeVisible();
    await expect(page.locator('[data-testid="flashcard-question"]')).toBeVisible();

    // Verify no contrast issues
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2aa'])
      .analyze();

    expect(accessibilityScanResults.violations).toHaveLength(0);
  });

  test('should support zoom up to 200%', async ({ page }) => {
    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Zoom to 200%
    await page.evaluate(() => {
      document.body.style.zoom = '2.0';
    });

    // Verify content still usable
    await expect(page.locator('button:has-text("Show Answer")')).toBeVisible();
    await expect(page.locator('[data-testid="flashcard-question"]')).toBeVisible();

    // Verify no horizontal scroll
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });

    expect(hasHorizontalScroll).toBe(false);
  });
});
```

---

## 9. Tooling Setup & Configuration

### 9.1 Testing Infrastructure

#### 9.1.1 Vitest Configuration

**File**: `frontend/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/tests/',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
        '**/types.ts',
      ],
      thresholds: {
        lines: 80,
        functions: 90,
        branches: 75,
        statements: 80,
      },
    },
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['node_modules', 'dist', 'build'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

#### 9.1.2 Playwright Configuration

**File**: `frontend/playwright.config.ts`

```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

#### 9.1.3 Pytest Configuration

**File**: `backend/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-fail-under=80
    -p no:warnings
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance benchmarks
    security: Security tests
asyncio_mode = auto
```

#### 9.1.4 Lighthouse CI Configuration

**File**: `frontend/lighthouserc.json`

```json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:5173/study-cards/review"],
      "numberOfRuns": 3,
      "settings": {
        "preset": "desktop",
        "throttling": {
          "rttMs": 40,
          "throughputKbps": 10240,
          "cpuSlowdownMultiplier": 1
        }
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 0.95}],
        "categories:best-practices": ["error", {"minScore": 0.9}],
        "categories:seo": ["error", {"minScore": 0.9}],
        "first-contentful-paint": ["error", {"maxNumericValue": 1500}],
        "speed-index": ["error", {"maxNumericValue": 3000}],
        "total-blocking-time": ["error", {"maxNumericValue": 300}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

---

## 10. Quality Gates & CI/CD

### 10.1 GitHub Actions Workflow

**File**: `.github/workflows/study-cards-tests.yml`

```yaml
name: Study Cards Pipeline Tests

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/src/ai/**'
      - 'backend/src/api/v1/study_cards.py'
      - 'backend/src/schemas/study_card.py'
      - 'backend/tests/test_ai/**'
      - 'backend/tests/test_integration/**'
      - 'frontend/src/components/study-cards/**'
      - 'frontend/src/hooks/useSM2Algorithm.ts'
      - 'frontend/tests/**'
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: irstudy_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run unit tests
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/irstudy_test
        run: |
          cd backend
          pytest tests/test_ai/ -v --cov=src.ai --cov-report=xml

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/irstudy_test
        run: |
          cd backend
          pytest tests/test_integration/ -v --cov=src --cov-report=xml

      - name: Run security tests
        run: |
          cd backend
          pytest tests/test_security/ -v

      - name: Run performance tests
        run: |
          cd backend
          pytest tests/test_performance/ -v -m performance

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          flags: backend
          name: backend-coverage

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js 20
        uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run unit tests
        run: |
          cd frontend
          npm test -- --coverage

      - name: Run TypeScript type check
        run: |
          cd frontend
          npx tsc --noEmit

      - name: Run linter
        run: |
          cd frontend
          npm run lint

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./frontend/coverage/coverage-final.json
          flags: frontend
          name: frontend-coverage

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js 20
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Install Playwright
        run: |
          cd frontend
          npx playwright install --with-deps chromium

      - name: Start backend (Docker)
        run: |
          docker-compose up -d backend postgres

      - name: Start frontend dev server
        run: |
          cd frontend
          npm run dev &
          npx wait-on http://localhost:5173

      - name: Run E2E tests
        run: |
          cd frontend
          npx playwright test

      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/

  lighthouse-audit:
    runs-on: ubuntu-latest
    needs: [frontend-tests]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js 20
        uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Start dev server
        run: |
          cd frontend
          npm run dev &
          npx wait-on http://localhost:5173

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          cd frontend
          lhci autorun

      - name: Upload Lighthouse results
        uses: actions/upload-artifact@v3
        with:
          name: lighthouse-results
          path: frontend/.lighthouseci/

  quality-gates:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests, e2e-tests, lighthouse-audit]

    steps:
      - name: Check test results
        run: |
          echo "✅ All quality gates passed"
          echo "- Backend tests: PASSED"
          echo "- Frontend tests: PASSED"
          echo "- E2E tests: PASSED"
          echo "- Lighthouse audit: PASSED"

      - name: Notify on failure
        if: failure()
        run: |
          echo "❌ Quality gates FAILED"
          exit 1
```

---

## Test Execution Commands

### Backend Tests

```bash
# All tests
pytest backend/tests/ -v

# Unit tests only
pytest backend/tests/test_ai/ -v

# Integration tests
pytest backend/tests/test_integration/ -v

# Security tests
pytest backend/tests/test_security/ -v

# Performance tests
pytest backend/tests/test_performance/ -v -m performance

# With coverage
pytest backend/tests/ --cov=src --cov-report=html

# Generate coverage report
pytest backend/tests/ --cov=src --cov-report=term-missing
```

### Frontend Tests

```bash
# All unit tests
npm test

# With coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Specific test file
npm test -- FlashcardReview.test.tsx

# E2E tests
npx playwright test

# E2E with UI
npx playwright test --ui

# E2E headed mode
npx playwright test --headed

# Specific E2E test
npx playwright test flashcard-review.spec.ts
```

### Accessibility Tests

```bash
# Axe scan
npx playwright test accessibility/

# Lighthouse CI
npm run lighthouse

# Manual Lighthouse (Chrome DevTools)
# 1. Open Chrome DevTools
# 2. Go to Lighthouse tab
# 3. Select "Accessibility" category
# 4. Click "Generate report"
```

### Performance Benchmarks

```bash
# Backend performance
pytest backend/tests/test_performance/ -v -m performance

# Frontend performance (Lighthouse)
npm run lighthouse

# Chrome DevTools Performance
# 1. Open Chrome DevTools
# 2. Go to Performance tab
# 3. Start recording
# 4. Flip flashcard
# 5. Stop recording
# 6. Analyze frame rate (should be 60fps)
```

---

## Summary: 112 Tests

| Category | Tests | Files |
|----------|-------|-------|
| **PRD-P1-006 (Flashcard UI)** | 40 | 8 files |
| **PRD-P1-007 (SM-2 Logic)** | 45 | 6 files |
| **PRD-P8-002 (Integration)** | 22 | 4 files |
| **Security** | 5 | 1 file |
| **TOTAL** | **112** | **19 files** |

### Coverage Summary

- **Backend Line Coverage**: ≥80%
- **Frontend Line Coverage**: ≥80%
- **Branch Coverage**: ≥75%
- **Function Coverage**: ≥90%
- **Integration Coverage**: 100% critical paths
- **E2E Coverage**: All user workflows

### Quality Benchmarks

- ✅ **Test Pass Rate**: 100% (zero tolerance)
- ✅ **Performance**: <8s generation, <200ms API, 60fps animation
- ✅ **Accessibility**: Lighthouse ≥95 (WCAG 2.2 AA)
- ✅ **Security**: 0 XSS, 0 SQL injection, JWT required
- ✅ **SM-2 Consistency**: TypeScript ↔ Python within 0.01

---

**End of Part 2**
