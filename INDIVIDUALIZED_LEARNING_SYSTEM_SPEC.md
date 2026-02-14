# Individualized Learning System - Technical Specification

## 1. System Overview

This document specifies the technical implementation of the adaptive learning system for the AMC Prep Platform, including:
- Student profiling and knowledge modeling
- Adaptive question selection algorithms
- Personalized study plan generation
- Progress tracking and analytics
- Achievement system

---

## 2. Database Schema

### 2.1 User Profile Tables

```sql
-- Core user profile with learning preferences
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Demographics
    country_of_origin VARCHAR(100),
    years_since_graduation INTEGER,
    previous_amc_attempts INTEGER DEFAULT 0,
    clinical_experience_years DECIMAL(3,1),
    english_proficiency VARCHAR(20) CHECK (english_proficiency IN ('basic', 'intermediate', 'advanced', 'native')),
    
    -- Study preferences
    study_hours_per_week INTEGER,
    target_exam_date DATE,
    preferred_study_time VARCHAR(20) CHECK (preferred_study_time IN ('morning', 'afternoon', 'evening', 'mixed')),
    session_length_preference INTEGER, -- minutes
    difficulty_preference VARCHAR(20) CHECK (difficulty_preference IN ('easy', 'medium', 'hard', 'adaptive')),
    
    -- Calculated fields
    days_until_exam INTEGER GENERATED ALWAYS AS (target_exam_date - CURRENT_DATE) STORED,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);

-- Knowledge state tracking
CREATE TABLE user_knowledge_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Overall metrics
    baseline_score DECIMAL(5,2), -- Diagnostic exam score
    current_percentile DECIMAL(5,2),
    exam_readiness_score DECIMAL(5,2),
    estimated_amc_score INTEGER, -- 3-digit score prediction
    
    -- Topic-level tracking (stored as JSON for flexibility)
    topic_proficiency JSONB DEFAULT '{}', -- { "cardiology": 0.75, "respiratory": 0.82 }
    
    -- Skill breakdown
    clinical_reasoning_score DECIMAL(5,2),
    knowledge_recall_score DECIMAL(5,2),
    guideline_application_score DECIMAL(5,2),
    prioritization_score DECIMAL(5,2),
    
    -- Calculated categorizations
    strength_areas JSONB DEFAULT '[]', -- Topics with >80% accuracy
    weakness_areas JSONB DEFAULT '[]', -- Topics with <60% accuracy
    unseen_topics JSONB DEFAULT '[]', -- Topics not yet attempted
    
    last_calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);

-- Learning behavior analytics
CREATE TABLE user_learning_behavior (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Time analytics
    avg_time_per_question DECIMAL(6,2), -- seconds
    avg_time_easy DECIMAL(6,2),
    avg_time_medium DECIMAL(6,2),
    avg_time_hard DECIMAL(6,2),
    best_performance_time VARCHAR(20),
    
    -- Engagement metrics
    explanation_reading_rate DECIMAL(5,2), -- 0-1
    revision_frequency DECIMAL(4,1), -- days between reviews
    skip_rate DECIMAL(5,2), -- questions skipped
    bookmark_rate DECIMAL(5,2),
    
    -- Consistency
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    total_study_days INTEGER DEFAULT 0,
    consistency_score DECIMAL(5,2), -- 0-100
    
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);

-- Performance history
CREATE TABLE user_performance_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    total_questions_answered INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    overall_accuracy DECIMAL(5,2),
    
    -- Weekly snapshots (for trend analysis)
    weekly_snapshots JSONB DEFAULT '[]', -- Array of {week: "2026-W01", accuracy: 0.75, questions: 150}
    
    -- Improvement tracking
    weekly_accuracy_change DECIMAL(5,2), -- percentage points
    learning_velocity DECIMAL(5,2), -- questions mastered per week
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);
```

### 2.2 Question Interaction Tables

```sql
-- Spaced repetition system (SRS) cards
CREATE TABLE srs_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR(100) NOT NULL,
    
    -- SRS parameters (SM-2 algorithm)
    interval_days INTEGER DEFAULT 1,
    ease_factor DECIMAL(3,2) DEFAULT 2.5,
    repetitions INTEGER DEFAULT 0,
    
    -- Scheduling
    next_review_date DATE NOT NULL,
    last_reviewed_at TIMESTAMP,
    
    -- History
    review_history JSONB DEFAULT '[]', -- [{date, rating, time_spent}]
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'mastered')),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, question_id)
);

-- Question attempts (audit trail)
CREATE TABLE question_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR(100) NOT NULL,
    session_id UUID, -- Groups attempts by study session
    
    -- Answer details
    user_answer VARCHAR(10) NOT NULL,
    correct_answer VARCHAR(10) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    
    -- Timing
    time_spent_seconds INTEGER,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Context
    study_mode VARCHAR(50), -- "adaptive", "exam", "weakness", "random"
    device_type VARCHAR(20), -- "web", "ios", "android"
    
    -- User actions
    read_explanation BOOLEAN DEFAULT false,
    clicked_citations BOOLEAN DEFAULT false,
    bookmarked BOOLEAN DEFAULT false,
    flagged BOOLEAN DEFAULT false,
    
    -- Sync status
    synced_at TIMESTAMP, -- For offline support
    
    INDEX idx_user_question (user_id, question_id),
    INDEX idx_user_date (user_id, answered_at)
);

-- Study sessions
CREATE TABLE study_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    
    -- Session metrics
    questions_answered INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    accuracy DECIMAL(5,2),
    
    -- Configuration
    session_type VARCHAR(50), -- "daily_queue", "exam_simulation", "topic_focus"
    target_topic VARCHAR(100),
    planned_questions INTEGER,
    
    -- Device info
    device_type VARCHAR(20),
    app_version VARCHAR(20),
    
    INDEX idx_user_sessions (user_id, started_at DESC)
);
```

### 2.3 Study Plans

```sql
-- Generated study plans
CREATE TABLE study_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Plan configuration
    exam_date DATE NOT NULL,
    study_hours_per_week INTEGER,
    total_hours DECIMAL(6,1),
    
    -- Plan structure
    phases JSONB NOT NULL, -- Array of phase objects
    milestones JSONB DEFAULT '[]',
    
    -- Progress
    current_phase INTEGER DEFAULT 0,
    completion_percentage DECIMAL(5,2) DEFAULT 0,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'abandoned')),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_active (user_id, status)
);

-- Study plan phase details
CREATE TABLE study_plan_phases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES study_plans(id) ON DELETE CASCADE,
    
    phase_number INTEGER,
    name VARCHAR(100),
    duration_weeks INTEGER,
    
    -- Content
    focus_areas JSONB, -- Array of topics
    daily_questions_target INTEGER,
    study_mode VARCHAR(50),
    
    -- Progress
    start_date DATE,
    end_date DATE,
    completion_percentage DECIMAL(5,2) DEFAULT 0,
    
    status VARCHAR(20) DEFAULT 'pending'
);
```

### 2.4 Achievements

```sql
-- Achievement definitions
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    achievement_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50), -- "learning", "accuracy", "consistency", "mastery", "special"
    
    -- Criteria
    criteria_type VARCHAR(50), -- "count", "threshold", "streak", "unique"
    criteria_value INTEGER,
    criteria_parameters JSONB, -- Flexible criteria definition
    
    -- Rewards
    points INTEGER DEFAULT 0,
    badge_url VARCHAR(500),
    
    -- Display
    icon VARCHAR(50),
    color VARCHAR(20),
    rarity VARCHAR(20) DEFAULT 'common' CHECK (rarity IN ('common', 'rare', 'epic', 'legendary')),
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User achievements
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    achievement_id VARCHAR(50) REFERENCES achievements(achievement_id),
    
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress_percentage DECIMAL(5,2) DEFAULT 100, -- For multi-step achievements
    
    UNIQUE(user_id, achievement_id)
);

-- User points/leaderboard
CREATE TABLE user_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    total_points INTEGER DEFAULT 0,
    lifetime_points INTEGER DEFAULT 0,
    points_by_category JSONB DEFAULT '{}',
    
    current_rank INTEGER,
    percentile DECIMAL(5,2),
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id)
);
```

---

## 3. Adaptive Question Selection Algorithm

### 3.1 Algorithm Implementation

```python
# backend/services/adaptive_engine.py

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, date, timedelta
import random
from enum import Enum

class QuestionMode(Enum):
    ADAPTIVE = "adaptive"
    RANDOM = "random"
    WEAKNESS = "weakness"
    EXAM = "exam"
    SRS = "srs"

@dataclass
class Question:
    id: str
    topic: str
    subtopic: str
    difficulty: str
    specialty: str
    last_seen: Optional[datetime]
    times_seen: int
    accuracy_history: List[bool]

class AdaptiveQuestionEngine:
    """
    Core engine for personalized question selection
    """
    
    def __init__(self, db, cache, srs_service):
        self.db = db
        self.cache = cache
        self.srs = srs_service
        
        # AMC Blueprint distribution
        self.amc_distribution = {
            "Adult Health": 0.35,
            "Women's Health": 0.15,
            "Child Health": 0.12,
            "Mental Health": 0.12,
            "Population Health": 0.08,
            "Surgery": 0.18
        }
    
    async def generate_daily_queue(
        self,
        user_id: str,
        queue_size: int = 30,
        mode: QuestionMode = QuestionMode.ADAPTIVE,
        focus_topics: Optional[List[str]] = None
    ) -> List[Question]:
        """
        Generate personalized question queue
        """
        # Get user profile
        profile = await self.get_user_profile(user_id)
        knowledge_state = await self.get_knowledge_state(user_id)
        
        if mode == QuestionMode.ADAPTIVE:
            return await self._adaptive_selection(
                user_id, profile, knowledge_state, queue_size, focus_topics
            )
        elif mode == QuestionMode.RANDOM:
            return await self._random_selection(user_id, queue_size, focus_topics)
        elif mode == QuestionMode.WEAKNESS:
            return await self._weakness_focused(user_id, knowledge_state, queue_size)
        elif mode == QuestionMode.EXAM:
            return await self._exam_simulation(user_id, queue_size)
        elif mode == QuestionMode.SRS:
            return await self._srs_only(user_id, queue_size)
    
    async def _adaptive_selection(
        self,
        user_id: str,
        profile: Dict,
        knowledge_state: Dict,
        count: int,
        focus_topics: Optional[List[str]]
    ) -> List[Question]:
        """
        Smart adaptive selection:
        40% SRS due cards
        30% Weakness targeting
        20% New content
        10% Strength maintenance
        """
        questions = []
        selected_ids = set()
        
        # 1. Spaced Repetition (40%)
        srs_count = int(count * 0.4)
        srs_cards = await self.srs.get_due_cards(user_id, limit=srs_count)
        for card in srs_cards:
            q = await self.get_question_by_id(card.question_id)
            if q:
                questions.append(q)
                selected_ids.add(q.id)
        
        # 2. Weakness Targeting (30%)
        weakness_count = int(count * 0.3)
        weak_topics = focus_topics or knowledge_state.get("weakness_areas", [])[:3]
        
        if weak_topics:
            weakness_questions = await self.db.get_questions(
                topics=weak_topics,
                exclude_ids=list(selected_ids),
                limit=weakness_count,
                min_difficulty="medium"
            )
            for q in weakness_questions:
                if q.id not in selected_ids:
                    questions.append(q)
                    selected_ids.add(q.id)
        
        # 3. New Content (20%)
        new_count = int(count * 0.2)
        unseen_topics = knowledge_state.get("unseen_topics", [])[:2]
        
        if unseen_topics:
            new_questions = await self.db.get_questions(
                topics=unseen_topics,
                exclude_ids=list(selected_ids),
                limit=new_count
            )
            for q in new_questions:
                if q.id not in selected_ids:
                    questions.append(q)
                    selected_ids.add(q.id)
        
        # 4. Strength Maintenance (10%)
        remaining = count - len(questions)
        if remaining > 0:
            strong_topics = knowledge_state.get("strength_areas", [])[:1]
            if strong_topics:
                maintenance = await self.db.get_questions(
                    topics=strong_topics,
                    exclude_ids=list(selected_ids),
                    limit=remaining
                )
                for q in maintenance:
                    if q.id not in selected_ids:
                        questions.append(q)
                        selected_ids.add(q.id)
        
        # 5. Fill remainder with random if needed
        remaining = count - len(questions)
        if remaining > 0:
            random_qs = await self.db.get_random_questions(
                exclude_ids=list(selected_ids),
                limit=remaining
            )
            questions.extend(random_qs)
        
        # Shuffle to prevent pattern recognition
        random.shuffle(questions)
        
        # Log selection for analytics
        await self.log_question_selection(user_id, questions, "adaptive")
        
        return questions[:count]
    
    async def _exam_simulation(
        self,
        user_id: str,
        count: int = 150
    ) -> List[Question]:
        """
        Generate questions matching AMC MCQ exam distribution
        """
        questions = []
        
        for category, percentage in self.amc_distribution.items():
            category_count = int(count * percentage)
            category_questions = await self.db.get_questions_by_category(
                category=category,
                limit=category_count,
                randomize=True
            )
            questions.extend(category_questions)
        
        # Shuffle to mix categories
        random.shuffle(questions)
        
        return questions[:count]
    
    async def calculate_difficulty_adjustment(
        self,
        user_id: str,
        topic: str
    ) -> str:
        """
        Determine appropriate difficulty based on user's performance
        """
        stats = await self.db.get_topic_stats(user_id, topic)
        
        accuracy = stats.get("accuracy", 0)
        attempts = stats.get("attempts", 0)
        
        if attempts < 5:
            return "medium"  # Not enough data
        
        if accuracy >= 0.85:
            return "hard"
        elif accuracy >= 0.70:
            return "medium"
        else:
            return "easy"
```

### 3.2 Spaced Repetition System (SM-2 Algorithm)

```python
# backend/services/srs_service.py

from datetime import datetime, date, timedelta
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class SRSCard:
    id: str
    user_id: str
    question_id: str
    interval_days: int
    ease_factor: float
    repetitions: int
    next_review_date: date
    last_reviewed_at: Optional[datetime]

class SRSService:
    """
    SuperMemo-2 algorithm implementation
    """
    
    # Rating scale
    AGAIN = 1  # Complete blackout
    HARD = 2   # Incorrect but recognized
    GOOD = 3   # Correct with difficulty
    EASY = 4   # Correct with ease
    
    async def review_card(
        self,
        card: SRSCard,
        rating: int,
        time_spent_seconds: int
    ) -> SRSCard:
        """
        Update card based on review rating
        """
        # Update ease factor
        card.ease_factor = self._update_ease_factor(card.ease_factor, rating)
        
        if rating < self.GOOD:
            # Failed review - reset
            card.repetitions = 0
            card.interval_days = 1
        else:
            # Successful review
            card.repetitions += 1
            
            if card.repetitions == 1:
                card.interval_days = 1
            elif card.repetitions == 2:
                card.interval_days = 6
            else:
                # I(n) = I(n-1) * EF
                card.interval_days = int(card.interval_days * card.ease_factor)
        
        # Cap interval at 365 days
        card.interval_days = min(card.interval_days, 365)
        
        # Update review date
        card.next_review_date = date.today() + timedelta(days=card.interval_days)
        card.last_reviewed_at = datetime.now()
        
        # Save to database
        await self.save_card(card)
        
        return card
    
    def _update_ease_factor(self, ef: float, rating: int) -> float:
        """
        Update ease factor using SM-2 formula
        EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        """
        q = rating
        new_ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        
        # Minimum ease factor of 1.3
        return max(1.3, new_ef)
    
    async def get_due_cards(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[SRSCard]:
        """
        Get cards due for review today
        """
        today = date.today()
        
        cards = await self.db.query("""
            SELECT * FROM srs_cards
            WHERE user_id = $1
              AND next_review_date <= $2
              AND status = 'active'
            ORDER BY next_review_date ASC, interval_days DESC
            LIMIT $3
        """, user_id, today, limit)
        
        return [self._to_card(row) for row in cards]
```

---

## 4. Progress Analytics Engine

### 4.1 Analytics Calculation

```python
# backend/services/analytics_engine.py

from typing import Dict, List
from datetime import datetime, date, timedelta
import statistics

class AnalyticsEngine:
    """
    Calculate user progress metrics and insights
    """
    
    async def calculate_user_dashboard(
        self,
        user_id: str
    ) -> Dict:
        """
        Generate complete analytics dashboard
        """
        # Get raw data
        attempts = await self.get_attempts(user_id, days=90)
        profile = await self.get_profile(user_id)
        
        return {
            "overall": await self._calculate_overall_metrics(user_id, attempts),
            "by_topic": await self._calculate_topic_metrics(user_id, attempts),
            "by_skill": await self._calculate_skill_metrics(user_id, attempts),
            "time_analytics": await self._calculate_time_metrics(user_id, attempts),
            "improvement": await self._calculate_improvement(user_id, attempts),
            "comparison": await self._calculate_comparison(user_id),
        }
    
    async def _calculate_overall_metrics(
        self,
        user_id: str,
        attempts: List[Dict]
    ) -> Dict:
        """
        Calculate high-level performance metrics
        """
        if not attempts:
            return {
                "total_questions": 0,
                "total_correct": 0,
                "accuracy": 0,
                "exam_readiness": 0
            }
        
        total = len(attempts)
        correct = sum(1 for a in attempts if a["is_correct"])
        accuracy = correct / total if total > 0 else 0
        
        # Calculate exam readiness score
        # Weighted combination of accuracy, consistency, and coverage
        consistency = await self._calculate_consistency(user_id)
        coverage = await self._calculate_coverage(user_id)
        
        readiness = (
            accuracy * 0.5 +
            consistency * 0.3 +
            coverage * 0.2
        ) * 100
        
        # Estimate AMC score (simplified model)
        # Real implementation would use ML model
        estimated_amc_score = self._estimate_amc_score(accuracy, total)
        
        return {
            "total_questions_attempted": total,
            "total_correct": correct,
            "overall_accuracy": round(accuracy * 100, 1),
            "exam_readiness_score": round(readiness, 1),
            "estimated_amc_score": estimated_amc_score,
            "percentile_rank": await self._get_percentile(user_id, accuracy)
        }
    
    async def _calculate_topic_metrics(
        self,
        user_id: str,
        attempts: List[Dict]
    ) -> List[Dict]:
        """
        Calculate per-topic performance
        """
        topic_stats = {}
        
        for attempt in attempts:
            topic = attempt.get("topic", "Unknown")
            
            if topic not in topic_stats:
                topic_stats[topic] = {
                    "attempts": 0,
                    "correct": 0,
                    "recent_attempts": []
                }
            
            topic_stats[topic]["attempts"] += 1
            if attempt["is_correct"]:
                topic_stats[topic]["correct"] += 1
            
            # Keep last 10 attempts for trend
            topic_stats[topic]["recent_attempts"].append({
                "date": attempt["answered_at"],
                "correct": attempt["is_correct"]
            })
        
        # Calculate metrics for each topic
        results = []
        for topic, stats in topic_stats.items():
            accuracy = stats["correct"] / stats["attempts"] if stats["attempts"] > 0 else 0
            
            # Determine trend
            recent = stats["recent_attempts"][-5:]
            if len(recent) >= 3:
                recent_accuracy = sum(1 for r in recent if r["correct"]) / len(recent)
                if recent_accuracy > accuracy + 0.1:
                    trend = "improving"
                elif recent_accuracy < accuracy - 0.1:
                    trend = "declining"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"
            
            # Determine strength category
            if accuracy >= 0.80:
                strength = "strong"
            elif accuracy >= 0.60:
                strength = "moderate"
            else:
                strength = "weak"
            
            results.append({
                "topic": topic,
                "questions_attempted": stats["attempts"],
                "accuracy": round(accuracy * 100, 1),
                "trend": trend,
                "strength": strength,
                "last_practiced": max(r["date"] for r in stats["recent_attempts"])
            })
        
        # Sort by accuracy (ascending) to show weakest first
        results.sort(key=lambda x: x["accuracy"])
        
        return results
    
    def _estimate_amc_score(self, accuracy: float, total_attempts: int) -> int:
        """
        Estimate AMC 3-digit score based on performance
        
        AMC MCQ: 150 questions, scaled to 500-point scale
        Pass: ~235-250 (varies by exam)
        Average: ~250-280
        High: 300+
        """
        if total_attempts < 100:
            return 0  # Insufficient data
        
        # Base score on accuracy
        # 60% accuracy ≈ 250 (pass)
        # 70% accuracy ≈ 280
        # 80% accuracy ≈ 310
        # 90% accuracy ≈ 350
        
        base_score = 150 + (accuracy * 250)
        
        # Adjust for volume (more questions = more reliable)
        volume_bonus = min((total_attempts - 100) / 100, 20)
        
        return int(base_score + volume_bonus)
```

---

## 5. Achievement System

### 5.1 Achievement Engine

```python
# backend/services/achievement_engine.py

from typing import List, Dict
from datetime import datetime

class AchievementEngine:
    """
    Track and award achievements
    """
    
    def __init__(self, db):
        self.db = db
        self.achievements = self._load_achievements()
    
    async def check_achievements(
        self,
        user_id: str,
        event: str,
        event_data: Dict
    ) -> List[Dict]:
        """
        Check if any achievements unlocked based on event
        """
        unlocked = []
        
        for achievement in self.achievements:
            if await self._meets_criteria(user_id, achievement, event, event_data):
                if not await self._already_earned(user_id, achievement["id"]):
                    await self._award_achievement(user_id, achievement)
                    unlocked.append(achievement)
        
        return unlocked
    
    async def _meets_criteria(
        self,
        user_id: str,
        achievement: Dict,
        event: str,
        event_data: Dict
    ) -> bool:
        """
        Check if user meets achievement criteria
        """
        criteria_type = achievement["criteria_type"]
        criteria_value = achievement["criteria_value"]
        params = achievement.get("criteria_parameters", {})
        
        if criteria_type == "count":
            # Count-based (e.g., answer 100 questions)
            current_count = await self._get_count(user_id, params["entity"], params.get("filters"))
            return current_count >= criteria_value
        
        elif criteria_type == "threshold":
            # Threshold-based (e.g., reach 80% accuracy)
            current_value = await self._get_metric(user_id, params["metric"])
            return current_value >= criteria_value
        
        elif criteria_type == "streak":
            # Streak-based (e.g., study 7 days in a row)
            current_streak = await self._get_streak(user_id, params["activity"])
            return current_streak >= criteria_value
        
        elif criteria_type == "unique":
            # Unique items (e.g., master 5 different topics)
            unique_count = await self._get_unique_count(user_id, params["entity"], params.get("threshold", 0.8))
            return unique_count >= criteria_value
        
        return False
    
    async def calculate_progress(
        self,
        user_id: str,
        achievement_id: str
    ) -> Dict:
        """
        Calculate progress toward an achievement
        """
        achievement = await self.get_achievement(achievement_id)
        criteria_type = achievement["criteria_type"]
        criteria_value = achievement["criteria_value"]
        params = achievement.get("criteria_parameters", {})
        
        if criteria_type == "count":
            current = await self._get_count(user_id, params["entity"], params.get("filters"))
            progress = min(current / criteria_value * 100, 100)
        
        elif criteria_type == "threshold":
            current = await self._get_metric(user_id, params["metric"])
            progress = min(current / criteria_value * 100, 100)
        
        elif criteria_type == "streak":
            current = await self._get_streak(user_id, params["activity"])
            progress = min(current / criteria_value * 100, 100)
        
        elif criteria_type == "unique":
            current = await self._get_unique_count(user_id, params["entity"], params.get("threshold", 0.8))
            progress = min(current / criteria_value * 100, 100)
        
        return {
            "achievement_id": achievement_id,
            "current_value": current,
            "target_value": criteria_value,
            "progress_percentage": round(progress, 1),
            "is_complete": progress >= 100
        }

# Predefined achievements
DEFAULT_ACHIEVEMENTS = [
    {
        "id": "first_steps",
        "name": "First Steps",
        "description": "Answer your first 10 questions",
        "category": "learning",
        "criteria_type": "count",
        "criteria_value": 10,
        "criteria_parameters": {"entity": "questions_answered"},
        "points": 50,
        "rarity": "common"
    },
    {
        "id": "centurion",
        "name": "Centurion",
        "description": "Answer 100 questions",
        "category": "learning",
        "criteria_type": "count",
        "criteria_value": 100,
        "criteria_parameters": {"entity": "questions_answered"},
        "points": 150,
        "rarity": "common"
    },
    {
        "id": "scholar",
        "name": "Scholar",
        "description": "Answer 1,000 questions",
        "category": "learning",
        "criteria_type": "count",
        "criteria_value": 1000,
        "criteria_parameters": {"entity": "questions_answered"},
        "points": 500,
        "rarity": "rare"
    },
    {
        "id": "high_performer",
        "name": "High Performer",
        "description": "Achieve 80% accuracy",
        "category": "accuracy",
        "criteria_type": "threshold",
        "criteria_value": 80,
        "criteria_parameters": {"metric": "overall_accuracy"},
        "points": 300,
        "rarity": "rare"
    },
    {
        "id": "dedicated",
        "name": "Dedicated",
        "description": "Study 14 days in a row",
        "category": "consistency",
        "criteria_type": "streak",
        "criteria_value": 14,
        "criteria_parameters": {"activity": "daily_study"},
        "points": 200,
        "rarity": "rare"
    },
    {
        "id": "cardiologist",
        "name": "Cardiologist",
        "description": "Achieve 90% accuracy in Cardiology",
        "category": "mastery",
        "criteria_type": "unique",
        "criteria_value": 1,
        "criteria_parameters": {"entity": "topic_accuracy", "topic": "Cardiology", "threshold": 0.9},
        "points": 400,
        "rarity": "epic"
    },
    {
        "id": "all_rounder",
        "name": "All-Rounder",
        "description": "Achieve 80% accuracy in all specialties",
        "category": "mastery",
        "criteria_type": "unique",
        "criteria_value": 6,  # Number of specialties
        "criteria_parameters": {"entity": "topic_accuracy", "threshold": 0.8},
        "points": 1000,
        "rarity": "legendary"
    }
]
```

---

## 6. API Endpoints

### 6.1 Question API

```python
# backend/api/questions.py

from fastapi import APIRouter, Depends, Query
from typing import List, Optional

router = APIRouter()

@router.get("/questions/daily-queue")
async def get_daily_queue(
    user: User = Depends(get_current_user),
    count: int = Query(30, ge=1, le=50),
    mode: str = Query("adaptive", enum=["adaptive", "random", "weakness", "exam"]),
    focus_topics: Optional[List[str]] = Query(None),
    engine: AdaptiveQuestionEngine = Depends(get_question_engine)
) -> QuestionQueueResponse:
    """
    Get personalized daily question queue
    """
    questions = await engine.generate_daily_queue(
        user_id=user.id,
        queue_size=count,
        mode=QuestionMode(mode),
        focus_topics=focus_topics
    )
    
    return QuestionQueueResponse(
        questions=[QuestionResponse.from_model(q) for q in questions],
        mode=mode,
        total_available=await engine.get_available_count(user.id),
        estimated_time_minutes=count * 2  # 2 min per question avg
    )

@router.post("/questions/{question_id}/answer")
async def submit_answer(
    question_id: str,
    answer: AnswerSubmission,
    user: User = Depends(get_current_user),
    srs_service: SRSService = Depends(get_srs_service),
    achievement_engine: AchievementEngine = Depends(get_achievement_engine)
):
    """
    Submit answer and update learning state
    """
    # Verify answer
    question = await get_question(question_id)
    is_correct = answer.selected_option == question.correct_answer
    
    # Record attempt
    attempt = await record_attempt(
        user_id=user.id,
        question_id=question_id,
        answer=answer,
        is_correct=is_correct,
        time_spent=answer.time_spent_seconds
    )
    
    # Update SRS if applicable
    srs_card = await srs_service.get_card(user.id, question_id)
    if srs_card:
        rating = srs_service.GOOD if is_correct else srs_service.AGAIN
        await srs_service.review_card(srs_card, rating, answer.time_spent_seconds)
    
    # Check achievements
    unlocked = await achievement_engine.check_achievements(
        user.id,
        "question_answered",
        {"correct": is_correct, "topic": question.topic}
    )
    
    # Update analytics
    await update_user_stats(user.id, attempt)
    
    return AnswerResponse(
        is_correct=is_correct,
        correct_answer=question.correct_answer,
        explanation=question.explanation,
        citations=question.citations,
        unlocked_achievements=unlocked,
        next_question_recommended=await get_next_recommendation(user.id)
    )
```

### 6.2 Analytics API

```python
# backend/api/analytics.py

@router.get("/analytics/dashboard")
async def get_dashboard(
    user: User = Depends(get_current_user),
    analytics_engine: AnalyticsEngine = Depends(get_analytics_engine)
) -> DashboardResponse:
    """
    Get complete analytics dashboard
    """
    dashboard = await analytics_engine.calculate_user_dashboard(user.id)
    return DashboardResponse(**dashboard)

@router.get("/analytics/topic/{topic_id}")
async def get_topic_analytics(
    topic_id: str,
    user: User = Depends(get_current_user)
) -> TopicAnalyticsResponse:
    """
    Get detailed analytics for specific topic
    """
    stats = await get_topic_stats(user.id, topic_id)
    return TopicAnalyticsResponse(
        topic=topic_id,
        accuracy=stats.accuracy,
        trend=stats.trend,
        weak_subtopics=stats.weak_subtopics,
        recommended_questions=stats.recommended_questions
    )
```

### 6.3 Study Plan API

```python
# backend/api/study_plans.py

@router.post("/study-plans/generate")
async def generate_study_plan(
    config: StudyPlanConfig,
    user: User = Depends(get_current_user),
    plan_generator: StudyPlanGenerator = Depends(get_plan_generator)
) -> StudyPlanResponse:
    """
    Generate personalized study plan
    """
    plan = await plan_generator.generate_study_plan(
        user_id=user.id,
        exam_date=config.exam_date,
        study_hours_per_week=config.study_hours_per_week
    )
    
    return StudyPlanResponse.from_model(plan)

@router.get("/study-plans/current")
async def get_current_plan(
    user: User = Depends(get_current_user)
) -> Optional[StudyPlanResponse]:
    """
    Get user's active study plan
    """
    plan = await get_active_plan(user.id)
    if not plan:
        raise HTTPException(status_code=404, detail="No active study plan")
    
    return StudyPlanResponse.from_model(plan)

@router.post("/study-plans/{plan_id}/progress")
async def update_plan_progress(
    plan_id: str,
    progress: PlanProgressUpdate,
    user: User = Depends(get_current_user)
) -> StudyPlanResponse:
    """
    Update study plan based on actual progress
    """
    plan = await get_plan(plan_id)
    if plan.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Adjust plan based on progress
    adjusted = await adjust_plan(plan, progress)
    
    return StudyPlanResponse.from_model(adjusted)
```

---

## 7. Frontend Integration

### 7.1 React Hooks

```typescript
// hooks/useAdaptiveQueue.ts
import { useQuery, useMutation } from '@tanstack/react-query';

export function useAdaptiveQueue(mode: 'adaptive' | 'exam' = 'adaptive') {
  const { data, isLoading } = useQuery({
    queryKey: ['daily-queue', mode],
    queryFn: () => api.getDailyQueue({ mode }),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const submitAnswer = useMutation({
    mutationFn: ({ questionId, answer }: { questionId: string; answer: Answer }) =>
      api.submitAnswer(questionId, answer),
    onSuccess: (data) => {
      // Show achievement notifications
      if (data.unlockedAchievements?.length > 0) {
        data.unlockedAchievements.forEach(achievement => {
          toast.success(`Achievement Unlocked: ${achievement.name}!`);
        });
      }
    }
  });

  return {
    questions: data?.questions || [],
    isLoading,
    submitAnswer: submitAnswer.mutate,
  };
}

// hooks/useProgress.ts
export function useProgress() {
  const { data } = useQuery({
    queryKey: ['dashboard'],
    queryFn: api.getDashboard,
    refetchInterval: 1000 * 60 * 5, // Refresh every 5 minutes
  });

  return {
    overall: data?.overall,
    byTopic: data?.byTopic,
    bySkill: data?.bySkill,
    timeAnalytics: data?.timeAnalytics,
    improvement: data?.improvement,
    comparison: data?.comparison,
  };
}

// hooks/useStudyPlan.ts
export function useStudyPlan() {
  const { data: plan } = useQuery({
    queryKey: ['study-plan'],
    queryFn: api.getCurrentPlan,
  });

  const generatePlan = useMutation({
    mutationFn: (config: StudyPlanConfig) => api.generateStudyPlan(config),
  });

  return {
    plan,
    generatePlan: generatePlan.mutate,
    currentPhase: plan?.phases[plan.currentPhase],
    progress: plan?.completionPercentage,
  };
}
```

### 7.2 Dashboard Components

```typescript
// components/ProgressDashboard.tsx
export function ProgressDashboard() {
  const { overall, byTopic, bySkill } = useProgress();

  return (
    <div className="space-y-6">
      {/* Overall Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          title="Questions Answered"
          value={overall?.totalQuestionsAttempted}
          icon={<BookOpen />}
        />
        <StatCard
          title="Overall Accuracy"
          value={`${overall?.overallAccuracy}%`}
          trend={overall?.overallAccuracy > 70 ? 'good' : 'needs-improvement'}
        />
        <StatCard
          title="Exam Readiness"
          value={`${overall?.examReadinessScore}%`}
          progressBar
        />
        <StatCard
          title="Estimated AMC Score"
          value={overall?.estimatedAMCScore}
          subtitle={`Pass: ~235-250`}
        />
      </div>

      {/* Topic Coverage Radar */}
      <Card>
        <CardHeader>Topic Performance</CardHeader>
        <CardContent>
          <TopicRadarChart data={byTopic} />
        </CardContent>
      </Card>

      {/* Weak Areas Alert */}
      {byTopic?.filter(t => t.strength === 'weak').length > 0 && (
        <Alert variant="warning">
          <AlertTitle>Focus Areas Detected</AlertTitle>
          <AlertDescription>
            You have {byTopic.filter(t => t.strength === 'weak').length} topics 
            that need attention. Consider switching to "Weakness Mode" for 
            targeted practice.
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}

// components/AchievementNotification.tsx
export function AchievementNotification({ achievement }: { achievement: Achievement }) {
  return (
    <div className="flex items-center gap-4 p-4 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-lg text-white">
      <Trophy className="w-12 h-12" />
      <div>
        <h4 className="font-bold text-lg">Achievement Unlocked!</h4>
        <p className="text-white/90">{achievement.name}</p>
        <p className="text-sm text-white/70">{achievement.description}</p>
        <Badge className="mt-2">+{achievement.points} points</Badge>
      </div>
    </div>
  );
}
```

---

## 8. Performance Optimization

### 8.1 Caching Strategy

```python
# backend/cache/strategies.py

class CacheStrategies:
    """
    Multi-tier caching for performance
    """
    
    # Redis cache TTLs
    USER_PROFILE_TTL = 3600  # 1 hour
    QUESTION_TTL = 86400  # 24 hours (questions don't change)
    DASHBOARD_TTL = 300  # 5 minutes
    DAILY_QUEUE_TTL = 60  # 1 minute
    
    async def get_user_dashboard_cached(self, user_id: str) -> Dict:
        """
        Get dashboard with caching
        """
        cache_key = f"dashboard:{user_id}"
        
        # Try cache first
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Calculate fresh
        dashboard = await self.analytics_engine.calculate_user_dashboard(user_id)
        
        # Cache for 5 minutes
        await redis.setex(
            cache_key,
            self.DASHBOARD_TTL,
            json.dumps(dashboard)
        )
        
        return dashboard
    
    async def invalidate_user_cache(self, user_id: str):
        """
        Invalidate all cached data for user (after answer submission)
        """
        patterns = [
            f"dashboard:{user_id}",
            f"daily-queue:{user_id}:*",
            f"knowledge-state:{user_id}",
        ]
        
        for pattern in patterns:
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
```

### 8.2 Database Optimization

```sql
-- Indexes for common queries
CREATE INDEX CONCURRENTLY idx_attempts_user_date 
ON question_attempts(user_id, answered_at DESC);

CREATE INDEX CONCURRENTLY idx_attempts_user_topic 
ON question_attempts(user_id, topic);

CREATE INDEX CONCURRENTLY idx_srs_due 
ON srs_cards(user_id, next_review_date) 
WHERE status = 'active';

CREATE INDEX CONCURRENTLY idx_achievements_user 
ON user_achievements(user_id, earned_at DESC);

-- Partition large tables
CREATE TABLE question_attempts_partitioned (
    LIKE question_attempts INCLUDING ALL
) PARTITION BY RANGE (answered_at);

-- Create monthly partitions
CREATE TABLE question_attempts_2026_01 
PARTITION OF question_attempts_partitioned
FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

```python
# tests/test_adaptive_engine.py

import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def adaptive_engine():
    db = AsyncMock()
    cache = AsyncMock()
    srs = AsyncMock()
    return AdaptiveQuestionEngine(db, cache, srs)

@pytest.mark.asyncio
async def test_adaptive_selection_ratio(adaptive_engine):
    """
    Test that adaptive selection follows correct ratios:
    40% SRS, 30% weakness, 20% new, 10% maintenance
    """
    user_id = "test-user"
    queue_size = 30
    
    # Mock dependencies
    adaptive_engine.srs.get_due_cards.return_value = [
        Mock(question_id=f"srs-{i}") for i in range(12)  # 40%
    ]
    adaptive_engine.db.get_questions.side_effect = [
        [Mock(id=f"weak-{i}") for i in range(9)],   # 30%
        [Mock(id=f"new-{i}") for i in range(6)],    # 20%
        [Mock(id=f"maint-{i}") for i in range(3)],  # 10%
    ]
    
    questions = await adaptive_engine.generate_daily_queue(
        user_id, queue_size, QuestionMode.ADAPTIVE
    )
    
    assert len(questions) == queue_size

@pytest.mark.asyncio
async def test_srs_algorithm():
    """
    Test SM-2 algorithm implementation
    """
    srs = SRSService(Mock())
    
    card = SRSCard(
        id="1",
        user_id="user-1",
        question_id="q-1",
        interval_days=1,
        ease_factor=2.5,
        repetitions=0,
        next_review_date=date.today(),
        last_reviewed_at=None
    )
    
    # Test successful review
    reviewed = await srs.review_card(card, srs.GOOD, 30)
    assert reviewed.repetitions == 1
    assert reviewed.interval_days == 1
    
    # Second successful review
    reviewed = await srs.review_card(reviewed, srs.GOOD, 25)
    assert reviewed.repetitions == 2
    assert reviewed.interval_days == 6
```

---

## 10. Deployment Checklist

### Pre-Launch

- [ ] Database migrations applied
- [ ] Indexes created
- [ ] Redis cache configured
- [ ] SRS algorithm validated
- [ ] Achievement system seeded
- [ ] Analytics engine tested
- [ ] Dashboard UI responsive
- [ ] Offline mode working (mobile)
- [ ] Rate limiting enabled

### Post-Launch Monitoring

- [ ] Queue generation performance (<200ms)
- [ ] Answer submission latency (<100ms)
- [ ] Dashboard load time (<1s)
- [ ] Cache hit rate (>80%)
- [ ] Error rate (<0.1%)
- [ ] User engagement metrics

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-31  
**Status**: Ready for Implementation
