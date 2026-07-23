# Project Engine Design: DSir

## 1. Overview

The Project Engine manages real-world projects that learners build to apply concepts. It handles project definitions, starter templates, submissions, automated and AI-assisted reviews, and portfolio generation.

## 2. Goals

- Provide authentic, portfolio-worthy projects
- Align projects with course concepts and career roadmaps
- Give actionable feedback through automated tests and AI review
- Support iterative improvement and resubmission

## 3. Project Types

- **Guided Projects:** Step-by-step with checkpoints
- **Unguided Projects:** Open-ended with requirements
- **Portfolio Projects:** Capstone projects demonstrating multiple skills
- **Mini Projects:** Short, focused projects for a single concept

## 4. Project Definition

Each project includes:

- Title and description
- Learning objectives
- Required and recommended concepts
- Acceptance criteria
- Starter files and templates
- Test cases or evaluation rubric
- Difficulty level
- Estimated duration

## 5. Project Lifecycle

1. **Discovery:** Learner browses and selects a project
2. **Setup:** Learner receives starter files and instructions
3. **Development:** Learner writes code in the browser or locally
4. **Submission:** Learner submits code or repository URL
5. **Evaluation:** Automated tests and AI review run
6. **Feedback:** Learner receives scores and suggestions
7. **Iteration:** Learner improves and resubmits
8. **Completion:** Project is marked complete and added to portfolio

## 6. Evaluation

### Automated Evaluation

- Unit tests
- Integration tests
- Linting and formatting checks
- Static analysis

### AI Review

- Code quality and style
- Architecture and design
- Edge case handling
- Documentation
- Suggestions for improvement

## 7. Submission Model

```
ProjectSubmission
  - user_id
  - project_id
  - repository_url
  - files
  - test_results
  - ai_feedback
  - score
  - submitted_at
  - reviewed_at
```

## 8. Portfolio

Completed projects can be exported as a portfolio:

- Public portfolio page
- Project descriptions and links
- Skills demonstrated
- AI-generated project summaries
- Shareable URL

## 9. Integration

- Reads concept mastery to recommend projects
- Writes submissions to the Assessment domain
- Triggers AI review via the AI domain
- Updates learner progress and mastery

## 10. Future Enhancements

- GitHub integration for repository submissions
- Peer review
- Project templates marketplace
- Industry partner projects
