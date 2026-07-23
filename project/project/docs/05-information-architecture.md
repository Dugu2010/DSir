# Information Architecture: DSir

## 1. Overview

DSir's information architecture separates learning content, learner data, AI services, and platform operations into clear, modular domains. This supports scalability, maintainability, and future extensibility.

## 2. Top-Level Domains

### 2.1 Content Domain

Stores and serves courses, roadmaps, concepts, lessons, and projects. Content is versioned and metadata-rich to support personalization and AI adaptation.

### 2.2 Learner Domain

Tracks users, enrollments, progress, mastery, revision schedules, and coding history. This domain is learner-centric and privacy-sensitive.

### 2.3 Assessment Domain

Handles submissions, evaluations, feedback, and scores. Includes code submissions, quiz responses, project reviews, and AI-generated assessments.

### 2.4 AI Domain

Provides provider-agnostic AI services: mentoring, code review, content generation, and adaptive recommendations. Isolates AI provider details from business logic.

### 2.5 Revision Domain

Manages spaced repetition schedules, revision queues, and adaptive problem selection. Works closely with the Assessment and Mastery domains.

### 2.6 Project Domain

Manages project definitions, templates, submissions, reviews, and portfolio outputs.

### 2.7 Platform Domain

Handles authentication, authorization, notifications, billing, analytics, and admin operations.

## 3. Navigation Structure

### Public
- Landing page
- Course catalog
- Roadmap catalog
- Pricing
- About / Blog

### Authenticated
- Dashboard
- My Learning
  - Current roadmap/course
  - Concepts
  - Lessons
  - Projects
- Revision Queue
- AI Mentor Chat
- Portfolio
- Profile & Settings

### Instructor
- Classes
- Learner progress
- Assignments
- Feedback

### Admin
- User management
- Content management
- AI configuration
- Analytics
- System health

## 4. Content Hierarchy

```
Roadmap
  └── Course (technology)
        └── Module (logical grouping)
              └── Concept (discrete learning objective)
                    └── Lesson (instructional unit)
                    └── Exercise (practice)
                    └── Assessment (check for understanding)
        └── Project (real-world application)
```

## 5. Data Flow

1. Learner enrolls in a roadmap
2. Platform generates a personalized learning plan
3. Learner completes lessons and exercises
4. Submissions are evaluated and stored
5. Mastery engine updates concept mastery
6. Revision engine schedules future reviews
7. AI mentor uses learner history to provide guidance
8. Projects are submitted, reviewed, and added to portfolio

## 6. API Organization

- `/api/v1/auth` - Authentication
- `/api/v1/users` - User management
- `/api/v1/courses` - Courses and content
- `/api/v1/roadmaps` - Roadmaps
- `/api/v1/enrollments` - Enrollments and progress
- `/api/v1/lessons` - Lessons and exercises
- `/api/v1/submissions` - Code and quiz submissions
- `/api/v1/revision` - Revision queue and scheduling
- `/api/v1/mastery` - Mastery tracking
- `/api/v1/projects` - Projects
- `/api/v1/ai` - AI mentor and code review
- `/api/v1/admin` - Admin operations
