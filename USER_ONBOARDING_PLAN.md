# User Onboarding Plan - irStudy MVP

**Date**: 2026-05-25
**Status**: Ready to Execute
**Duration**: 2-3 days
**Prerequisites**: Integration Testing Complete (0 blockers)

---

## Executive Summary

This document outlines the user onboarding strategy for the irStudy MVP platform. The goal is to create a seamless first-time user experience that guides medical students through platform features, demonstrates value quickly, and establishes long-term engagement patterns.

**Success Criteria**:
- ✅ New users complete registration in <2 minutes
- ✅ 80% of new users complete first practice session within 5 minutes
- ✅ Users understand all 4 modules (MCQ, OSCE, EMR, Mock Exam)
- ✅ Help documentation covers 100% of common questions
- ✅ Demo data provides immediate value without requiring activity
- ✅ Onboarding checklist drives engagement to 3+ modules

---

## 1. Onboarding Journey Map

### Stage 1: Discovery & Registration (2 minutes)

```
Landing Page → Sign Up → Email Verification → Profile Setup → Welcome Tour
```

**User Goals**:
- Understand what irStudy offers
- Create account quickly
- Verify email address
- Complete basic profile

**Platform Goals**:
- Communicate value proposition clearly
- Minimize registration friction
- Capture essential user data
- Set expectations for platform features

---

### Stage 2: First Session (5 minutes)

```
Welcome Tour → Dashboard Overview → First Practice Session → Results Review → Next Steps
```

**User Goals**:
- See immediate value from platform
- Complete first successful activity
- Understand how scoring works
- Know what to do next

**Platform Goals**:
- Demonstrate educational quality
- Build confidence with easy wins
- Establish habit loop (practice → feedback → improvement)
- Guide to next activity

---

### Stage 3: Feature Discovery (15 minutes)

```
Explore Modules → Try OSCE → Convert to EMR → View Progress → Review Recommendations
```

**User Goals**:
- Understand all available features
- See how modules integrate
- Track personal progress
- Identify areas for improvement

**Platform Goals**:
- Showcase unique features (OSCE → EMR conversion)
- Demonstrate AI-powered recommendations
- Encourage multi-module usage
- Build engagement across features

---

### Stage 4: Habit Formation (7 days)

```
Daily Practice → Weekly Review → Mock Exam → Goal Setting → Specialty Focus
```

**User Goals**:
- Establish regular practice routine
- Prepare for real exams (AMC/FRACP)
- Focus on weak specialties
- Track improvement over time

**Platform Goals**:
- Drive daily active users (DAU)
- Increase retention rate
- Encourage premium features (mock exams)
- Build community engagement

---

## 2. Welcome Tour Implementation

### 2.1 Interactive Product Tour

**Technology**: Use [Shepherd.js](https://shepherdjs.dev/) or [Intro.js](https://introjs.com/)

**Tour Steps**:

```javascript
// File: frontend/src/components/onboarding/WelcomeTour.tsx

import { ShepherdTour } from 'react-shepherd';
import 'shepherd.js/dist/css/shepherd.css';

const tourSteps = [
  {
    id: 'welcome',
    title: 'Welcome to irStudy! 🎉',
    text: 'Your AI-powered platform for Australian medical exam preparation. Let\'s take a quick tour (2 minutes).',
    buttons: [
      {
        text: 'Start Tour',
        action: tour => tour.next()
      },
      {
        text: 'Skip',
        action: tour => tour.complete()
      }
    ]
  },
  {
    id: 'dashboard',
    title: 'Your Dashboard',
    text: 'Track your progress across all modules. See your scores, strengths, and personalized recommendations.',
    attachTo: { element: '.dashboard-overview', on: 'bottom' },
    buttons: [
      { text: 'Back', action: tour => tour.back() },
      { text: 'Next', action: tour => tour.next() }
    ]
  },
  {
    id: 'mcq-module',
    title: 'MCQ Practice',
    text: 'Practice with 1,600+ questions covering cardiology, respiratory, psychiatry, and more. Each question includes detailed explanations and Australian medical citations.',
    attachTo: { element: '.module-card-mcq', on: 'right' },
    buttons: [
      { text: 'Back', action: tour => tour.back() },
      { text: 'Next', action: tour => tour.next() }
    ]
  },
  {
    id: 'osce-module',
    title: 'OSCE Simulation',
    text: 'Practice clinical scenarios with AI-powered assessment. Complete history taking, physical exams, and receive detailed feedback on your approach.',
    attachTo: { element: '.module-card-osce', on: 'right' },
    buttons: [
      { text: 'Back', action: tour => tour.back() },
      { text: 'Next', action: tour => tour.next() }
    ]
  },
  {
    id: 'emr-module',
    title: 'EMR Practice',
    text: 'Write clinical notes in realistic EMR systems (Epic, Cerner, Best Practice). Get AI feedback on your documentation quality and clinical reasoning.',
    attachTo: { element: '.module-card-emr', on: 'left' },
    buttons: [
      { text: 'Back', action: tour => tour.back() },
      { text: 'Next', action: tour => tour.next() }
    ]
  },
  {
    id: 'mock-exam-module',
    title: 'Mock Exams',
    text: 'Simulate real AMC Part 1 and FRACP exams. Timed conditions, realistic difficulty, and comprehensive performance analysis.',
    attachTo: { element: '.module-card-mock-exam', on: 'left' },
    buttons: [
      { text: 'Back', action: tour => tour.back() },
      { text: 'Next', action: tour => tour.next() }
    ]
  },
  {
    id: 'specialty-breakdown',
    title: 'Specialty Performance',
    text: 'See how you perform across medical specialties. Focus your study on areas that need improvement.',
    attachTo: { element: '.specialty-breakdown-chart', on: 'top' },
    buttons: [
      { text: 'Back', action: tour => tour.back() },
      { text: 'Next', action: tour => tour.next() }
    ]
  },
  {
    id: 'recommendations',
    title: 'AI Recommendations',
    text: 'Get personalized study suggestions based on your performance, learning patterns, and exam preparation timeline.',
    attachTo: { element: '.recommendations-panel', on: 'top' },
    buttons: [
      { text: 'Back', action: tour => tour.back() },
      { text: 'Next', action: tour => tour.next() }
    ]
  },
  {
    id: 'start-practicing',
    title: 'Ready to Start!',
    text: 'Let\'s begin with a quick MCQ session to get you familiar with the platform. You\'ll answer 5 questions and see how our feedback system works.',
    buttons: [
      {
        text: 'Start First Session',
        action: (tour) => {
          tour.complete();
          window.location.href = '/mcq?onboarding=true';
        }
      }
    ]
  }
];

export const WelcomeTour: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  return (
    <ShepherdTour
      steps={tourSteps}
      tourOptions={{
        useModalOverlay: true,
        defaultStepOptions: {
          cancelIcon: { enabled: true },
          scrollTo: { behavior: 'smooth', block: 'center' }
        }
      }}
      onComplete={onComplete}
    />
  );
};
```

---

### 2.2 First MCQ Session (Guided)

**Objective**: Complete 5 easy questions with extra guidance

**Implementation**:

```typescript
// File: frontend/src/components/onboarding/GuidedMCQSession.tsx

import React, { useState } from 'react';
import { Box, Typography, Card, Button, Alert } from '@mui/material';
import { useMCQSession } from '../api/mcqs';

export const GuidedMCQSession: React.FC = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);

  const { data: questions } = useMCQSession({
    difficulty: 'easy',
    limit: 5,
    onboarding: true  // Flag to filter appropriate questions
  });

  const handleSubmit = () => {
    setShowFeedback(true);
  };

  const handleNext = () => {
    setShowFeedback(false);
    setSelectedAnswer(null);
    setCurrentQuestion(currentQuestion + 1);
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>First Session Guide:</strong> Take your time with each question.
          We'll show you detailed explanations and Australian medical references
          after each answer.
        </Typography>
      </Alert>

      <Card sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Question {currentQuestion + 1} of 5
        </Typography>

        <Typography variant="body1" sx={{ my: 2 }}>
          {questions?.[currentQuestion]?.question_text}
        </Typography>

        {/* Answer Options */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {Object.entries(questions?.[currentQuestion]?.options || {}).map(([key, value]) => (
            <Button
              key={key}
              variant={selectedAnswer === key ? 'contained' : 'outlined'}
              onClick={() => setSelectedAnswer(key)}
              disabled={showFeedback}
              sx={{
                justifyContent: 'flex-start',
                textAlign: 'left',
                textTransform: 'none'
              }}
            >
              <strong>{key}.</strong>&nbsp;{value}
            </Button>
          ))}
        </Box>

        {/* Submit Button */}
        {!showFeedback && (
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={!selectedAnswer}
            sx={{ mt: 2 }}
            fullWidth
          >
            Submit Answer
          </Button>
        )}

        {/* Feedback Section */}
        {showFeedback && (
          <Box sx={{ mt: 3 }}>
            <Alert severity={
              selectedAnswer === questions?.[currentQuestion]?.correct_answer
                ? 'success'
                : 'error'
            }>
              <Typography variant="h6">
                {selectedAnswer === questions?.[currentQuestion]?.correct_answer
                  ? '✅ Correct!'
                  : '❌ Incorrect'
                }
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                <strong>Correct Answer:</strong> {questions?.[currentQuestion]?.correct_answer}
              </Typography>
            </Alert>

            <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="subtitle2" color="primary" gutterBottom>
                Explanation
              </Typography>
              <Typography variant="body2">
                {questions?.[currentQuestion]?.explanation}
              </Typography>

              <Typography variant="subtitle2" color="primary" sx={{ mt: 2 }} gutterBottom>
                Reference
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {questions?.[currentQuestion]?.citation}
              </Typography>
            </Box>

            <Button
              variant="contained"
              onClick={handleNext}
              fullWidth
              sx={{ mt: 2 }}
            >
              {currentQuestion < 4 ? 'Next Question' : 'See Results'}
            </Button>
          </Box>
        )}
      </Card>
    </Box>
  );
};
```

---

### 2.3 Onboarding Checklist

**Objective**: Guide users to try all features with progress tracking

**Implementation**:

```typescript
// File: frontend/src/components/onboarding/OnboardingChecklist.tsx

import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  LinearProgress,
  Box,
  Chip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import { useOnboardingProgress } from '../api/onboarding';

export const OnboardingChecklist: React.FC = () => {
  const { data: progress } = useOnboardingProgress();

  const checklist = [
    {
      id: 'welcome_tour',
      label: 'Complete welcome tour',
      description: 'Learn about irStudy features',
      completed: progress?.welcome_tour_completed || false,
      points: 10
    },
    {
      id: 'first_mcq',
      label: 'Complete first MCQ session',
      description: 'Practice with multiple choice questions',
      completed: progress?.first_mcq_completed || false,
      points: 20
    },
    {
      id: 'first_osce',
      label: 'Try OSCE simulation',
      description: 'Practice clinical scenarios',
      completed: progress?.first_osce_completed || false,
      points: 30
    },
    {
      id: 'osce_to_emr',
      label: 'Convert OSCE to EMR case',
      description: 'Experience seamless integration',
      completed: progress?.osce_to_emr_completed || false,
      points: 20
    },
    {
      id: 'view_progress',
      label: 'Review your dashboard',
      description: 'Check your progress and recommendations',
      completed: progress?.dashboard_viewed || false,
      points: 10
    },
    {
      id: 'specialty_focus',
      label: 'Focus on a specialty',
      description: 'Complete 3 questions in one specialty',
      completed: progress?.specialty_focused || false,
      points: 10
    }
  ];

  const completedTasks = checklist.filter(task => task.completed).length;
  const totalTasks = checklist.length;
  const progressPercentage = (completedTasks / totalTasks) * 100;
  const totalPoints = checklist.reduce((sum, task) => sum + (task.completed ? task.points : 0), 0);

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Getting Started
          </Typography>
          <Chip
            label={`${totalPoints}/100 points`}
            color="primary"
            size="small"
          />
        </Box>

        <LinearProgress
          variant="determinate"
          value={progressPercentage}
          sx={{ mb: 2, height: 8, borderRadius: 4 }}
        />

        <Typography variant="body2" color="text.secondary" gutterBottom>
          {completedTasks} of {totalTasks} tasks completed
        </Typography>

        <List>
          {checklist.map((task) => (
            <ListItem
              key={task.id}
              sx={{
                opacity: task.completed ? 0.7 : 1,
                cursor: task.completed ? 'default' : 'pointer',
                '&:hover': {
                  bgcolor: task.completed ? 'transparent' : 'action.hover'
                }
              }}
            >
              <ListItemIcon>
                {task.completed ? (
                  <CheckCircleIcon color="success" />
                ) : (
                  <RadioButtonUncheckedIcon color="action" />
                )}
              </ListItemIcon>
              <ListItemText
                primary={task.label}
                secondary={task.description}
                primaryTypographyProps={{
                  sx: {
                    textDecoration: task.completed ? 'line-through' : 'none',
                    fontWeight: task.completed ? 400 : 500
                  }
                }}
              />
              <Chip
                label={`${task.points} pts`}
                size="small"
                variant={task.completed ? 'filled' : 'outlined'}
                color={task.completed ? 'success' : 'default'}
              />
            </ListItem>
          ))}
        </List>

        {progressPercentage === 100 && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
            <Typography variant="body2" color="success.dark">
              🎉 Congratulations! You've completed all onboarding tasks.
              You're ready to start your exam preparation journey!
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};
```

---

## 3. Help Documentation

### 3.1 In-App Help System

**Objective**: Provide contextual help at every step

**Implementation**:

```typescript
// File: frontend/src/components/help/HelpButton.tsx

import React, { useState } from 'react';
import {
  IconButton,
  Popover,
  Typography,
  Box,
  Link
} from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

interface HelpButtonProps {
  topic: string;
  content: string;
  learnMoreUrl?: string;
}

export const HelpButton: React.FC<HelpButtonProps> = ({
  topic,
  content,
  learnMoreUrl
}) => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);

  return (
    <>
      <IconButton
        size="small"
        onClick={(e) => setAnchorEl(e.currentTarget)}
        aria-label={`Help: ${topic}`}
      >
        <HelpOutlineIcon fontSize="small" />
      </IconButton>

      <Popover
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={() => setAnchorEl(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
      >
        <Box sx={{ p: 2, maxWidth: 400 }}>
          <Typography variant="subtitle2" gutterBottom>
            {topic}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {content}
          </Typography>
          {learnMoreUrl && (
            <Link
              href={learnMoreUrl}
              variant="body2"
              sx={{ mt: 1, display: 'block' }}
            >
              Learn more →
            </Link>
          )}
        </Box>
      </Popover>
    </>
  );
};

// Usage in components:
// <HelpButton
//   topic="MCQ Scoring"
//   content="Each question is worth 1 point. Your percentage is calculated as (correct answers / total questions) × 100."
//   learnMoreUrl="/help/mcq-scoring"
// />
```

---

### 3.2 FAQ Section

**Content Structure**:

```markdown
# Frequently Asked Questions

## Getting Started

### How do I create an account?
Click "Sign Up" on the landing page, enter your email and password, and verify your email address. You'll be guided through a welcome tour to learn about the platform.

### Is irStudy free?
We offer a free tier with access to 50 MCQs and 10 OSCE scenarios per month. Premium plans unlock unlimited practice, mock exams, and advanced analytics.

### What exams does irStudy prepare me for?
irStudy is designed for Australian medical exams including:
- AMC Part 1 (Multiple Choice Examination)
- AMC Clinical Examination
- FRACP Written Examination
- RACP Clinical Examination

## Practice Sessions

### How are MCQs scored?
Each MCQ is worth 1 point. Your percentage is calculated as (correct answers / total questions) × 100. We track your performance by specialty and difficulty level.

### What is an OSCE simulation?
OSCE (Objective Structured Clinical Examination) simulations let you practice clinical scenarios. You'll take a patient history, perform examinations, and receive AI-powered feedback on your clinical approach.

### Can I pause a session and resume later?
Yes! All your progress is auto-saved. You can close the browser and resume from where you left off.

### How do I convert an OSCE to an EMR case?
After completing an OSCE, click "Convert to EMR Case" on the results page. This transfers the patient scenario to an EMR practice environment where you can document your clinical findings.

## Progress Tracking

### What does the dashboard show?
Your dashboard displays:
- Total sessions completed across all modules
- Average scores by module and specialty
- Recent activity timeline
- Personalized recommendations for improvement

### How are recommendations generated?
Our AI analyzes your performance patterns, identifies weak specialties, and suggests targeted practice. Recommendations update daily based on your activity.

### Can I export my progress data?
Yes! Click "Export Data" on your dashboard to download your performance history as CSV or PDF.

## Technical Support

### Which browsers are supported?
irStudy works best on:
- Chrome (latest version)
- Firefox (latest version)
- Safari (latest version)
- Edge (latest version)

### I'm having trouble logging in
Try these steps:
1. Check your email and password are correct
2. Clear your browser cache and cookies
3. Try resetting your password
4. Contact support@irstudy.com.au if issues persist

### How do I report a bug?
Click the "Report Issue" button in the bottom-right corner, or email support@irstudy.com.au with:
- Description of the problem
- Steps to reproduce
- Screenshot (if applicable)

## Account Management

### How do I change my password?
Go to Settings → Account → Change Password

### How do I delete my account?
Go to Settings → Account → Delete Account. Note: This permanently deletes all your data and cannot be undone.

### Can I use irStudy on mobile?
Currently, irStudy is optimized for desktop browsers. A mobile app is planned for 2027.

## Contact & Support

### How do I contact support?
- Email: support@irstudy.com.au
- Live chat: Click the chat icon (Mon-Fri, 9am-5pm AEST)
- Help center: https://help.irstudy.com.au

### Where can I provide feedback?
We love feedback! Email feedback@irstudy.com.au or use the "Feedback" button in the app.
```

---

### 3.3 Video Tutorials

**Content Plan**:

| Video | Duration | Topics Covered | Priority |
|-------|----------|----------------|----------|
| **Platform Overview** | 3 min | Dashboard tour, module overview, navigation | P0 |
| **MCQ Practice Guide** | 5 min | Starting session, answering questions, reviewing explanations | P0 |
| **OSCE Simulation Tutorial** | 7 min | Choosing scenario, history taking, physical exam, scoring | P0 |
| **EMR Documentation** | 6 min | Writing SOAP notes, using templates, AI feedback | P1 |
| **Mock Exam Walkthrough** | 4 min | Starting exam, timer usage, reviewing results | P1 |
| **Progress Tracking** | 3 min | Reading dashboard metrics, interpreting recommendations | P1 |

**Video Hosting**: YouTube (unlisted) or Vimeo (password-protected)

**Implementation**:

```typescript
// File: frontend/src/components/help/VideoTutorials.tsx

import React from 'react';
import { Box, Card, CardContent, Typography, Grid } from '@mui/material';
import PlayCircleOutlineIcon from '@mui/icons-material/PlayCircleOutline';

const tutorials = [
  {
    id: 'platform-overview',
    title: 'Platform Overview',
    duration: '3 min',
    thumbnail: '/assets/video-thumbnails/platform-overview.jpg',
    videoUrl: 'https://www.youtube.com/embed/[VIDEO_ID]'
  },
  {
    id: 'mcq-guide',
    title: 'MCQ Practice Guide',
    duration: '5 min',
    thumbnail: '/assets/video-thumbnails/mcq-guide.jpg',
    videoUrl: 'https://www.youtube.com/embed/[VIDEO_ID]'
  },
  // ... more tutorials
];

export const VideoTutorials: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Video Tutorials
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Learn how to use irStudy with these quick video guides.
      </Typography>

      <Grid container spacing={3}>
        {tutorials.map((tutorial) => (
          <Grid item xs={12} sm={6} md={4} key={tutorial.id}>
            <Card
              sx={{
                cursor: 'pointer',
                '&:hover': { boxShadow: 3 }
              }}
              onClick={() => window.open(tutorial.videoUrl, '_blank')}
            >
              <Box sx={{ position: 'relative' }}>
                <img
                  src={tutorial.thumbnail}
                  alt={tutorial.title}
                  style={{ width: '100%', height: 200, objectFit: 'cover' }}
                />
                <PlayCircleOutlineIcon
                  sx={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    fontSize: 64,
                    color: 'white',
                    opacity: 0.9
                  }}
                />
              </Box>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {tutorial.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {tutorial.duration}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};
```

---

## 4. Demo Data Strategy

### 4.1 Pre-Populated Demo Account

**Objective**: Show value immediately without requiring user activity

**Implementation**:

```sql
-- Create demo user with realistic data
INSERT INTO users (id, email, password_hash, full_name, is_demo_account)
VALUES (
  'demo-user-uuid',
  'demo@irstudy.com.au',
  '[hashed-password]',
  'Demo Student',
  TRUE
);

-- Add 30 days of demo activity
-- MCQ sessions (20 sessions across specialties)
INSERT INTO mcq_attempts (user_id, mcq_id, selected_answer, is_correct, specialty, created_at)
SELECT
  'demo-user-uuid',
  mcq_id,
  CASE WHEN random() < 0.75 THEN correct_answer ELSE 'A' END,
  random() < 0.75,
  specialty,
  NOW() - (random() * INTERVAL '30 days')
FROM mcqs
ORDER BY random()
LIMIT 200;

-- OSCE sessions (10 sessions)
INSERT INTO osce_sessions (user_id, osce_id, score, status, created_at)
SELECT
  'demo-user-uuid',
  osce_id,
  7.0 + (random() * 2.5),  -- Scores 7.0-9.5
  'completed',
  NOW() - (random() * INTERVAL '30 days')
FROM osces
ORDER BY random()
LIMIT 10;

-- EMR sessions (5 sessions)
INSERT INTO emr_sessions (user_id, case_id, status, score, created_at)
SELECT
  'demo-user-uuid',
  case_id,
  'graded',
  70 + (random() * 25),  -- Scores 70-95
  NOW() - (random() * INTERVAL '30 days')
FROM patient_personas
ORDER BY random()
LIMIT 5;

-- Mock exam (1 completed exam)
INSERT INTO mock_exam_sessions (user_id, template_id, score, status, created_at)
VALUES (
  'demo-user-uuid',
  'amc-part-1-template',
  78.5,
  'completed',
  NOW() - INTERVAL '7 days'
);
```

**Frontend Detection**:

```typescript
// File: frontend/src/components/dashboard/DemoAccountBanner.tsx

import React from 'react';
import { Alert, Button } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

export const DemoAccountBanner: React.FC = () => {
  const { user } = useAuth();

  if (!user?.is_demo_account) return null;

  return (
    <Alert
      severity="info"
      action={
        <Button color="inherit" size="small" href="/signup">
          Create Account
        </Button>
      }
      sx={{ mb: 3 }}
    >
      You're viewing a demo account with sample data.
      Create a free account to track your own progress!
    </Alert>
  );
};
```

---

### 4.2 Sample Questions for Onboarding

**Objective**: Curate easy, high-quality questions for first session

**Selection Criteria**:
- ✅ Difficulty: EASY
- ✅ Specialty: General Practice or Cardiology
- ✅ High-quality explanations (>200 words)
- ✅ Australian context (eTG/PBS references)
- ✅ No images (simpler for first session)
- ✅ Clear correct answer (avoid controversial topics)

**Database Tag**:

```sql
-- Tag onboarding-appropriate MCQs
UPDATE mcqs
SET tags = array_append(tags, 'onboarding_suitable')
WHERE difficulty = 'easy'
  AND LENGTH(explanation) > 200
  AND citation LIKE '%eTG%'
  AND image_url IS NULL
  AND specialty IN ('general_practice', 'cardiology');

-- Verify count
SELECT COUNT(*) FROM mcqs WHERE 'onboarding_suitable' = ANY(tags);
-- Expected: 50-100 questions
```

---

## 5. Email Communication Strategy

### 5.1 Welcome Email Sequence

**Email 1: Account Verification** (Immediate)

```
Subject: Verify your irStudy account

Hi [First Name],

Welcome to irStudy! 🎉

Click the button below to verify your email and complete registration:

[Verify Email Button]

Once verified, you'll get access to:
✅ 1,600+ MCQs with Australian medical references
✅ 225 OSCE clinical scenarios
✅ AI-powered EMR documentation practice
✅ Full-length AMC and FRACP mock exams

Questions? Reply to this email or visit help.irstudy.com.au

Best regards,
The irStudy Team
```

---

**Email 2: Welcome Tour Reminder** (+2 hours after verification, if tour not completed)

```
Subject: Your irStudy tour is waiting

Hi [First Name],

You're all set up! Ready to explore irStudy?

We've created a 2-minute tour to show you around. You'll learn:
• How to practice MCQs with detailed explanations
• How OSCE simulations work
• How to track your progress across specialties

[Start Tour Button]

Already familiar with the platform? Jump straight to practice:
• MCQ Practice →
• OSCE Scenarios →
• Dashboard →

Happy studying,
The irStudy Team
```

---

**Email 3: First Session Completed** (Triggered after first MCQ/OSCE)

```
Subject: Great start, [First Name]! 🎯

Hi [First Name],

Congratulations on completing your first session!

Your score: [X/Y] ([Z]%)
Time spent: [N] minutes
Specialty: [Specialty]

What's next?
1. Try a different specialty to broaden your knowledge
2. Take an OSCE simulation for clinical practice
3. Review your dashboard to see personalized recommendations

[View Dashboard Button]

Keep up the momentum!
The irStudy Team
```

---

**Email 4: Week 1 Progress Summary** (+7 days)

```
Subject: Your first week on irStudy

Hi [First Name],

You've been on irStudy for a week. Here's your progress:

📊 Your Stats
• Total sessions: [X]
• Average score: [Y]%
• Time studied: [Z] hours
• Strongest specialty: [Specialty]

🎯 This Week's Goal
Complete 5 more sessions to unlock your first achievement badge!

💡 Recommended Next Steps
• [Personalized recommendation 1]
• [Personalized recommendation 2]

[Continue Practicing Button]

Questions? We're here to help: support@irstudy.com.au

Best regards,
The irStudy Team
```

---

### 5.2 Re-Engagement Emails

**Email: Inactive User (7 days without activity)**

```
Subject: We miss you, [First Name]

Hi [First Name],

We noticed you haven't practiced on irStudy this week.

Your progress so far:
• Sessions completed: [X]
• Current average: [Y]%
• Days until exam: [Z] (if set)

Quick 5-minute session?
We've picked some questions based on your weak areas:

[Start Quick Session Button]

Need help getting back on track? Reply to this email.

Best,
The irStudy Team
```

---

## 6. Onboarding Metrics & Analytics

### 6.1 Key Performance Indicators (KPIs)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Registration Completion Rate** | >90% | (Verified accounts / Started registrations) × 100 |
| **Tour Completion Rate** | >60% | (Completed tours / Logged in users) × 100 |
| **Time to First Session** | <5 min | Median time from login to first MCQ/OSCE |
| **First Session Completion** | >80% | (Finished first session / Started first session) × 100 |
| **Day 1 Retention** | >50% | Users who return within 24 hours |
| **Week 1 Retention** | >30% | Users active in first 7 days |
| **Onboarding Checklist Completion** | >40% | Users who complete 6/6 checklist tasks |
| **Multi-Module Adoption** | >50% | Users who try ≥2 different modules in first week |

---

### 6.2 Tracking Implementation

```typescript
// File: frontend/src/utils/analytics.ts

import mixpanel from 'mixpanel-browser';

// Initialize (use env variable)
mixpanel.init(import.meta.env.VITE_MIXPANEL_TOKEN);

export const trackOnboardingEvent = (event: string, properties?: Record<string, any>) => {
  mixpanel.track(`Onboarding: ${event}`, {
    ...properties,
    timestamp: new Date().toISOString()
  });
};

// Track specific events
export const onboardingEvents = {
  // Registration flow
  registrationStarted: () => trackOnboardingEvent('Registration Started'),
  registrationCompleted: (userId: string) => trackOnboardingEvent('Registration Completed', { userId }),
  emailVerified: (userId: string) => trackOnboardingEvent('Email Verified', { userId }),

  // Tour flow
  tourStarted: () => trackOnboardingEvent('Tour Started'),
  tourCompleted: () => trackOnboardingEvent('Tour Completed'),
  tourSkipped: (step: number) => trackOnboardingEvent('Tour Skipped', { step }),

  // First session
  firstSessionStarted: (module: string) => trackOnboardingEvent('First Session Started', { module }),
  firstSessionCompleted: (module: string, score: number) =>
    trackOnboardingEvent('First Session Completed', { module, score }),

  // Checklist
  checklistTaskCompleted: (taskId: string, points: number) =>
    trackOnboardingEvent('Checklist Task Completed', { taskId, points }),
  checklistFullyCompleted: () => trackOnboardingEvent('Checklist Fully Completed'),

  // Module adoption
  moduleExplored: (module: string) => trackOnboardingEvent('Module Explored', { module }),
  multiModuleUser: (modules: string[]) =>
    trackOnboardingEvent('Multi-Module User', { modulesUsed: modules.join(',') })
};
```

---

### 6.3 A/B Testing Opportunities

**Test 1: Tour Timing**
- **Variant A**: Show tour immediately after login (current plan)
- **Variant B**: Delay tour until after first session
- **Hypothesis**: Delaying tour reduces friction and increases first session completion
- **Metric**: First session completion rate

**Test 2: Onboarding Checklist Visibility**
- **Variant A**: Checklist always visible on dashboard (current plan)
- **Variant B**: Checklist in collapsible sidebar
- **Hypothesis**: Always-visible checklist increases task completion
- **Metric**: Checklist completion rate

**Test 3: Demo Account Promotion**
- **Variant A**: No demo account option (require registration)
- **Variant B**: "Try Demo" button on landing page
- **Hypothesis**: Demo account increases conversion by reducing signup friction
- **Metric**: Registration completion rate

---

## 7. Implementation Roadmap

### Phase 1: Core Onboarding (Day 1-2)

**Backend Tasks**:
- [ ] Create onboarding progress tracking table
- [ ] Build onboarding progress API endpoint
- [ ] Implement demo account creation script
- [ ] Add onboarding_suitable tags to MCQs

**Frontend Tasks**:
- [ ] Build WelcomeTour component (Shepherd.js)
- [ ] Build GuidedMCQSession component
- [ ] Build OnboardingChecklist component
- [ ] Add analytics tracking for onboarding events

**Estimated Time**: 12-16 hours

---

### Phase 2: Help Documentation (Day 2)

**Content Tasks**:
- [ ] Write FAQ content (20-30 questions)
- [ ] Create help page layout
- [ ] Build contextual HelpButton components
- [ ] Add help buttons to all major pages

**Frontend Tasks**:
- [ ] Build FAQ page with search
- [ ] Build HelpButton popover component
- [ ] Integrate help system into navigation

**Estimated Time**: 8-10 hours

---

### Phase 3: Email & Engagement (Day 3)

**Backend Tasks**:
- [ ] Set up email service (SendGrid/Mailgun)
- [ ] Create email templates (5 templates)
- [ ] Build email trigger system
- [ ] Implement re-engagement email logic

**Content Tasks**:
- [ ] Write all email copy
- [ ] Design email templates (HTML/CSS)
- [ ] Test email rendering across clients

**Estimated Time**: 6-8 hours

---

### Phase 4: Video Tutorials (Optional - can defer to post-launch)

**Production Tasks**:
- [ ] Script 6 video tutorials
- [ ] Record screen captures
- [ ] Edit videos (add captions, annotations)
- [ ] Upload to YouTube/Vimeo
- [ ] Embed videos in help center

**Estimated Time**: 12-16 hours (defer to post-launch)

---

## 8. Success Criteria

**Onboarding Implementation COMPLETE when**:

- ✅ Welcome tour functional with 8 steps
- ✅ Guided first session with 5 easy MCQs
- ✅ Onboarding checklist with 6 tasks
- ✅ FAQ page with ≥20 questions
- ✅ Contextual help buttons on all major pages
- ✅ 5 email templates created and tested
- ✅ Demo account with 30 days of activity
- ✅ Analytics tracking all onboarding events
- ✅ All KPIs measurable via dashboard
- ✅ Mobile responsiveness verified

**Target Launch Metrics**:
- Tour completion rate: >60%
- First session completion: >80%
- Day 1 retention: >50%
- Multi-module adoption: >50%

---

## 9. Testing Checklist

**Before Launch**:

- [ ] Test welcome tour on all browsers (Chrome, Firefox, Safari)
- [ ] Verify guided first session shows appropriate questions
- [ ] Confirm onboarding checklist updates correctly
- [ ] Test all help button popovers render correctly
- [ ] Send test emails to verify rendering
- [ ] Verify demo account has realistic data
- [ ] Confirm analytics events fire correctly
- [ ] Test mobile responsiveness for all onboarding flows
- [ ] User test onboarding with 3-5 external testers
- [ ] Fix all P0/P1 issues found in testing

---

**Document Version**: 1.0
**Last Updated**: 2026-05-25
**Next Review**: After implementation
**Owner**: Product Team
