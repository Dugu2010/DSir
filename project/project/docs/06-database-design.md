# Database Design: DSir

## 1. Overview

DSir uses PostgreSQL as the primary database. The schema is organized around domains: users, content, learning, assessment, revision, and AI. Redis is used for caching, sessions, and job queues.

## 2. Core Tables

### 2.1 Users & Roles

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    avatar_url TEXT,
    role VARCHAR(50) DEFAULT 'learner',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    timezone VARCHAR(50),
    daily_goal_minutes INTEGER DEFAULT 30,
    preferred_language VARCHAR(10) DEFAULT 'en',
    onboarding_completed BOOLEAN DEFAULT false,
    preferences JSONB DEFAULT '{}'
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    PRIMARY KEY (user_id, role)
);
```

### 2.2 Content

```sql
CREATE TABLE roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_published BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    technology VARCHAR(100) NOT NULL,
    is_published BOOLEAN DEFAULT false,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE roadmap_courses (
    roadmap_id UUID REFERENCES roadmaps(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    PRIMARY KEY (roadmap_id, course_id)
);

CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    slug VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    difficulty VARCHAR(50),
    prerequisites UUID[] DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(course_id, slug)
);

CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    slug VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    lesson_type VARCHAR(50) DEFAULT 'reading',
    position INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(concept_id, slug)
);
```

### 2.3 Learning & Progress

```sql
CREATE TABLE enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    roadmap_id UUID REFERENCES roadmaps(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    status VARCHAR(50) DEFAULT 'active',
    UNIQUE(user_id, roadmap_id, course_id)
);

CREATE TABLE concept_mastery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    score INTEGER DEFAULT 0,
    confidence INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    correct_streak INTEGER DEFAULT 0,
    last_reviewed_at TIMESTAMPTZ,
    next_review_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, concept_id)
);

CREATE TABLE user_activity (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2.4 Assessment

```sql
CREATE TABLE submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE SET NULL,
    concept_id UUID REFERENCES concepts(id) ON DELETE SET NULL,
    submission_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    evaluation JSONB,
    score INTEGER,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    evaluated_at TIMESTAMPTZ
);

CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    slug VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    requirements JSONB DEFAULT '{}',
    starter_files JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(course_id, slug)
);

CREATE TABLE project_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    repository_url TEXT,
    files JSONB,
    feedback JSONB,
    score INTEGER,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ
);
```

### 2.5 Revision

```sql
CREATE TABLE revision_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    concept_id UUID REFERENCES concepts(id) ON DELETE CASCADE,
    interval_days INTEGER DEFAULT 1,
    ease_factor REAL DEFAULT 2.5,
    due_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, concept_id)
);

CREATE TABLE revision_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    concepts UUID[] DEFAULT '{}',
    results JSONB DEFAULT '{}'
);
```

## 3. Indexing Strategy

- B-tree indexes on foreign keys and frequently filtered columns
- GIN indexes on JSONB metadata fields used in queries
- Partial indexes for published content
- BRIN or B-tree indexes on timestamp columns for activity feeds

## 4. Partitioning

- `user_activity` partitioned by range on `created_at`
- `submissions` partitioned by hash on `user_id`
- Consider partitioning revision tables by `user_id` at scale

## 5. Redis Usage

- Session storage
- Rate limiting counters
- Caching frequently accessed content
- Job queues for AI tasks and notifications
- Cached graph paths and revision queues
- Real-time leaderboards and streaks (optional)

## 6. Vector Extension

PostgreSQL uses the `pgvector` extension to store embeddings for:

- Learner history and mistake patterns
- Concept descriptions and lesson content
- Code submissions for similarity search
- AI context retrieval (RAG)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE concept_embeddings (
    concept_id UUID PRIMARY KEY REFERENCES concepts(id) ON DELETE CASCADE,
    embedding VECTOR(1536),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_concept_embeddings_embedding ON concept_embeddings USING hnsw (embedding vector_cosine_ops);
```
