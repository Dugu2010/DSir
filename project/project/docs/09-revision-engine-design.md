# Revision Engine Design: DSir

## 1. Overview

The Revision Engine schedules and delivers personalized revision sessions using spaced repetition, active recall, and adaptive scheduling. It ensures long-term retention by surfacing concepts at optimal intervals.

## 2. Goals

- Maximize long-term retention
- Prioritize weak concepts and recent mistakes
- Generate fresh problems to avoid rote memorization
- Adapt intervals based on learner performance
- Keep daily revision sessions short and focused

## 3. Scheduling Algorithm

The engine uses an adapted SM-2 algorithm:

```
if response_quality >= threshold:
    repetitions += 1
    interval = interval * ease_factor
else:
    repetitions = 0
    interval = base_interval

ease_factor = max(1.3, ease_factor + (0.1 - (5 - response_quality) * (0.08 + (5 - response_quality) * 0.02)))
```

- `response_quality`: 0-5 rating of the learner's answer
- `ease_factor`: How easy the concept is for the learner
- `interval`: Days until next review

## 4. Components

### 4.1 Scheduler

Computes the next review date for each concept based on the learner's performance.

### 4.2 Queue Builder

Builds the daily revision queue by selecting concepts that are due, prioritizing:
1. Overdue concepts
2. Weak concepts (low mastery)
3. Recently missed concepts
4. Concepts due today

### 4.3 Problem Generator

Generates fresh problems for each revision item. Problems are created by:
- Selecting from a bank of templated problems
- Varying parameters and context
- Using AI to generate novel problems when templates are exhausted

### 4.4 Session Manager

Tracks revision sessions, records results, and updates schedules.

## 5. Data Model

```
RevisionSchedule
  - user_id
  - concept_id
  - interval_days
  - ease_factor
  - due_at
  - last_reviewed_at

RevisionSession
  - user_id
  - started_at
  - completed_at
  - concepts
  - results
```

## 6. Revision Flow

1. Learner opens the revision queue
2. System selects due concepts
3. For each concept, a fresh problem is generated
4. Learner submits an answer
5. System evaluates the answer
6. Scheduler updates the next review date
7. Mastery engine updates concept mastery
8. Session is recorded

## 7. Pre-Computation

Revision problems are pre-computed asynchronously by background workers (Celery/RQ) during off-peak hours. This avoids AI latency during learner sessions and ensures a smooth experience.

```
RevisionProblemQueue
  - user_id
  - concept_id
  - problem_data
  - generated_at
  - expires_at
```

## 8. Adaptive Behavior

- If a learner answers correctly multiple times, the interval grows
- If a learner answers incorrectly, the interval resets and the concept is prioritized
- Difficulty and problem type adapt to the learner's mistake patterns
- Daily session length is capped to prevent overload

## 9. Fresh Problem Guarantee

To prevent memorization:
- Problems are parameterized and randomized
- Multiple problem templates exist per concept
- AI generates new variants when needed
- Learners never see the exact same problem twice

## 10. Integration

- Reads from `concept_mastery` and `submissions`
- Writes to `revision_schedules` and `revision_sessions`
- Triggers AI problem generation when templates are insufficient
- Notifies learners when revision is due
