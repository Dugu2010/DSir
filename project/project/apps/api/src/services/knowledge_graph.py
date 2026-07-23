from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.content import Concept, RoadmapCourse

if TYPE_CHECKING:
    pass


@dataclass
class GraphNode:
    concept_id: UUID
    title: str
    slug: str
    prerequisites: list[UUID] = field(default_factory=list)


@dataclass
class RoadmapGraph:
    roadmap_id: UUID
    courses: list[UUID]


class KnowledgeGraph:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_course_concepts(self, course_id: UUID) -> list[Concept]:
        result = await self.db.execute(
            select(Concept).where(Concept.course_id == course_id).order_by(Concept.created_at)
        )
        return list(result.scalars().all())

    async def build_concept_graph(self, course_id: UUID) -> dict[UUID, GraphNode]:
        concepts = await self.get_course_concepts(course_id)
        graph: dict[UUID, GraphNode] = {}
        for concept in concepts:
            graph[concept.id] = GraphNode(
                concept_id=concept.id,
                title=concept.title,
                slug=concept.slug,
                prerequisites=concept.prerequisites or [],
            )
        return graph

    async def get_prerequisites(self, concept_id: UUID) -> list[UUID]:
        result = await self.db.execute(select(Concept).where(Concept.id == concept_id))
        concept = result.scalar_one_or_none()
        if concept is None:
            return []
        return concept.prerequisites or []

    async def get_dependents(self, concept_id: UUID, course_id: UUID) -> list[UUID]:
        result = await self.db.execute(
            select(Concept).where(
                Concept.course_id == course_id,
                Concept.prerequisites.contains([concept_id]),
            )
        )
        return [c.id for c in result.scalars().all()]

    async def is_prereq_chain_satisfied(self, concept_id: UUID, mastered_concepts: set[UUID]) -> bool:
        prereqs = await self.get_prerequisites(concept_id)
        return set(prereqs).issubset(mastered_concepts)

    async def topological_sort(self, course_id: UUID) -> list[UUID]:
        graph = await self.build_concept_graph(course_id)
        in_degree: dict[UUID, int] = dict.fromkeys(graph, 0)
        for node in graph.values():
            for prereq in node.prerequisites:
                if prereq in in_degree:
                    in_degree[node.concept_id] += 1

        queue = deque([cid for cid, d in in_degree.items() if d == 0])
        ordered: list[UUID] = []
        while queue:
            current = queue.popleft()
            ordered.append(current)
            for cid, node in graph.items():
                if current in node.prerequisites and cid in in_degree:
                    in_degree[cid] -= 1
                    if in_degree[cid] == 0:
                        queue.append(cid)

        if len(ordered) != len(graph):
            raise ValueError("Cycle detected in concept graph")
        return ordered

    async def next_unlocked_concepts(self, course_id: UUID, mastered_concepts: set[UUID]) -> list[UUID]:
        graph = await self.build_concept_graph(course_id)
        unlocked = []
        for cid, node in graph.items():
            if cid in mastered_concepts:
                continue
            if set(node.prerequisites or []).issubset(mastered_concepts):
                unlocked.append(cid)
        return unlocked

    async def build_roadmap_graph(self, roadmap_id: UUID) -> RoadmapGraph:
        result = await self.db.execute(
            select(RoadmapCourse).where(RoadmapCourse.roadmap_id == roadmap_id).order_by(RoadmapCourse.position)
        )
        links = result.scalars().all()
        return RoadmapGraph(
            roadmap_id=roadmap_id,
            courses=[link.course_id for link in links],
        )

    async def generate_learning_path(
        self,
        roadmap_id: UUID,
        mastered_concepts: set[UUID],
    ) -> list[UUID]:
        roadmap_graph = await self.build_roadmap_graph(roadmap_id)
        path: list[UUID] = []
        for course_id in roadmap_graph.courses:
            ordered = await self.topological_sort(course_id)
            for concept_id in ordered:
                if concept_id not in mastered_concepts:
                    prereqs_satisfied = await self.is_prereq_chain_satisfied(concept_id, mastered_concepts)
                    if prereqs_satisfied:
                        path.append(concept_id)
        return path

    async def validate_prerequisites(self, concept_id: UUID, mastered_concepts: set[UUID]) -> bool:
        return await self.is_prereq_chain_satisfied(concept_id, mastered_concepts)
