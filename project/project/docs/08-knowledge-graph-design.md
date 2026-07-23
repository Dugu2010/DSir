# Knowledge Graph Design: DSir

## 1. Overview

The DSir knowledge graph models relationships between concepts, courses, roadmaps, and learner mastery. It enables personalized learning paths, prerequisite checking, and targeted revision.

## 2. Graph Entities

### Nodes

- **Concept:** A discrete learning objective (e.g., "Python Functions", "CSS Flexbox")
- **Course:** A collection of concepts for a single technology
- **Roadmap:** A sequence of courses toward a career goal
- **Project:** A real-world application of multiple concepts
- **Learner:** A user with mastery states

### Edges

- **Prerequisite:** Concept A must be mastered before Concept B
- **PartOf:** Concept belongs to Course; Course belongs to Roadmap
- **AppliesTo:** Project applies to multiple Concepts
- **MasteredBy:** Learner has mastery of Concept

## 3. Graph Storage

The graph is stored relationally in PostgreSQL using `concepts.prerequisites` and join tables. For advanced graph queries, a materialized view or adjacency list is used.

```sql
-- Concepts reference prerequisites as an array of concept IDs
-- Projects reference concepts via project_concepts join table
-- Roadmaps reference courses via roadmap_courses join table
```

## 4. Use Cases

### Prerequisite Checking
Before allowing a learner to start a concept, the system checks whether prerequisite concepts have sufficient mastery.

### Learning Path Generation
Given a learner's current mastery and goal, the graph is traversed to find the shortest valid path through concepts.

### Gap Analysis
When a learner struggles with a concept, the system identifies weak or missing prerequisites.

### Project Recommendations
Projects are recommended based on the set of concepts the learner has mastered or is ready to apply.

## 5. Graph Operations

| Operation | Implementation |
|-----------|----------------|
| Add concept | Insert concept with prerequisite IDs |
| Add prerequisite | Update `prerequisites` array |
| Find prerequisites | Recursive CTE or cached traversal |
| Find dependents | Recursive CTE on `prerequisites` |
| Validate path | Topological sort of concept graph |

## 6. Graph Caching

Valid learning paths and prerequisite chains are pre-computed and cached in Redis when a learner enrolls. This avoids expensive recursive CTEs during normal operation.

```
key: path:{user_id}:{roadmap_id}
value: ordered list of concept IDs

ttl: 24 hours or until mastery changes significantly
```

## 7. Example Concept Graph

```
Python Variables
       │
       ▼
Python Conditionals
       │
       ▼
Python Loops
       │
       ▼
Python Functions
       │
       ▼
Python Modules
```

## 8. Future Enhancements

- Migrate to a dedicated graph database (e.g., Neo4j) if query complexity grows
- Use embeddings to discover implicit relationships between concepts
- Visualize the knowledge graph for learners and instructors
