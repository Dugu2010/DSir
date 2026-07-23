# User Roles: DSir

## 1. Learner

The primary user. Learners enroll in courses and roadmaps, complete lessons, practice revision, build projects, and interact with the AI mentor.

**Permissions:**
- View and enroll in public courses and roadmaps
- Complete lessons and submit code
- Receive AI feedback and mentoring
- Track personal progress and mastery
- Manage profile and preferences

## 2. Instructor

Teachers, tutors, or mentors who guide groups of learners. Instructors can view learner progress, provide feedback, and assign content.

**Permissions:**
- All Learner permissions
- Create and manage classes/groups
- View aggregated progress of assigned learners
- Provide manual feedback on projects
- Assign specific lessons, projects, or revision sets

## 3. Content Creator

Authors and curriculum designers who create and maintain courses, lessons, concepts, and projects.

**Permissions:**
- Create and edit courses, roadmaps, concepts, and lessons
- Manage AI prompt templates for content
- Review and publish content
- Tag and organize content

## 4. Admin

Platform administrators responsible for user management, configuration, and overall platform health.

**Permissions:**
- Manage users and roles
- Configure AI providers and global settings
- View platform analytics
- Moderate content and interactions
- Manage integrations (SSO, LMS, etc.)

## 5. API Consumer

External applications or services that interact with DSir via API.

**Permissions:**
- Access granted via API keys
- Read/write permissions scoped to key purpose
- Rate-limited by plan

## 6. Anonymous Visitor

Unauthenticated users browsing public information.

**Permissions:**
- View public landing pages
- View course catalog (limited details)
- Sign up or log in

## Role Assignment

- Roles are stored per user and can be combined (e.g., a user can be both Learner and Content Creator)
- Role-based access control (RBAC) is enforced at the API layer
- Future support for custom roles and fine-grained permissions
