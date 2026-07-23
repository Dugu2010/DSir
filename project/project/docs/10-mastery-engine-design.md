# Mastery Engine Design: DSir

## 1. Overview

The Mastery Engine evaluates and tracks learner understanding at the concept level. It produces a mastery score, confidence score, and identifies strengths and weaknesses for each learner.

## 2. Goals

- Measure true understanding, not just completion
- Update mastery in real time based on evidence
- Identify misconceptions and weak areas
- Provide actionable insights to learners and instructors

## 3. Mastery Dimensions

For each concept, the engine tracks:

- **Mastery Score (0-100):** Overall understanding
- **Confidence (0-100):** How consistently the learner demonstrates mastery
- **Exposure Count:** Number of times the concept has been encountered
- **Correct Streak:** Consecutive correct responses
- **Attempt History:** Recent performance trend
- **Last Reviewed:** When the concept was last practiced

## 4. Evidence Sources

Mastery is updated based on:

- Lesson exercise submissions
- Coding problem submissions
- Quiz responses
- Revision session results
- Project submissions
- AI mentor interactions

## 5. Scoring Algorithm

Mastery is computed using a weighted Bayesian-like approach:

```
mastery = (evidence_score * evidence_weight) + (confidence_penalty)

where:
  evidence_score = average(correctness * difficulty_weight)
  confidence = function of correct_streak, exposure_count, recency
```

- Correct answers increase mastery, but gains diminish as mastery approaches 100
- Incorrect answers decrease mastery more when confidence was high
- Difficult problems and projects carry more weight than simple quizzes
- Mastery decays slowly over time if not practiced

## 6. Confidence Calculation

Confidence reflects the stability of the learner's mastery:

```
confidence = f(correct_streak, exposure_count, variance, recency)
```

- High confidence requires multiple correct responses across varied contexts
- Confidence decreases after incorrect answers or long gaps
- Confidence is used to determine readiness for advanced concepts

## 7. Strengths & Weaknesses

The engine identifies:

- **Strengths:** High mastery, high confidence concepts
- **Weaknesses:** Low mastery or low confidence concepts
- **At-Risk:** Concepts with decaying mastery or recent mistakes

These are surfaced on the dashboard and used by the AI mentor.

## 8. Decay

Mastery decays over time to reflect forgetting. Decay is applied by a nightly batch job rather than on every read or write:

```
decay_factor = e^(-lambda * days_since_review)
```

Decay is slower for high-confidence concepts and faster for newly learned concepts. The batch job updates `concept_mastery` rows and invalidates relevant caches.

## 9. Batch Job

A nightly Celery/RQ job:
- Applies decay to all concepts
- Identifies at-risk concepts
- Pre-generates revision problems for due concepts
- Warms caches for active learners

## 10. Integration

- Consumes events from the Assessment domain
- Updates `concept_mastery` table
- Provides data to the Revision Engine for scheduling
- Provides data to the AI mentor for personalization
- Powers dashboard visualizations

## 11. Future Enhancements

- Fine-grained subskill mastery
- Cross-concept transfer analysis
- Predictive models for dropout risk
