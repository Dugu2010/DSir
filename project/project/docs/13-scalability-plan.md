# Scalability Plan: DSir

## 1. Overview

DSir is designed to serve millions of learners while remaining efficient and cost-effective. Scalability is addressed at the application, data, and infrastructure layers.

## 2. Horizontal Scaling

- Backend services are stateless and run in Docker containers
- Load balancers distribute traffic across multiple instances
- Auto-scaling based on CPU, memory, and request queue depth

## 3. Database Scaling

- Read replicas for read-heavy workloads
- Connection pooling via PgBouncer
- Query optimization and indexing
- Partitioning for large tables (activity, submissions)
- Caching frequently accessed data in Redis

## 4. Caching Strategy

- Redis for session storage and rate limiting
- Content caching for published courses and lessons
- Mastery and revision queue caching per user
- CDN for static assets and uploaded files

## 5. Async Processing

- Celery or RQ for background jobs
- AI requests are queued to avoid blocking API responses
- Email and notification jobs processed asynchronously
- Code execution and project evaluation run in isolated workers

## 6. AI Cost Management

- Caching of common AI responses
- Token usage optimization
- Fallback to cheaper models for low-stakes tasks
- Mock provider for development and testing
- Rate limiting per user

## 7. Storage Scaling

- S3-compatible object storage for files, submissions, and assets
- Lifecycle policies for archival
- Multi-region replication for high availability

## 8. Microservices Readiness

The modular monolith is organized into clear domains. If a domain becomes a bottleneck, it can be extracted into a separate service:

- AI service
- Code execution service
- Revision service
- Notification service

## 9. Monitoring

- Application performance monitoring (APM)
- Database query performance monitoring
- AI provider latency and cost tracking
- Error tracking and alerting
- Capacity planning dashboards

## 10. Cost Optimization

- Use spot instances for background workers
- Optimize AI prompts to reduce token usage
- Cache aggressively
- Archive old data
- Monitor and right-size infrastructure
