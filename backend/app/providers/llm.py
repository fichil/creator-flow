from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TopicGenerationMaterial:
    id: int
    material_type: str
    title: str | None = None
    text_content: str | None = None
    source_url: str | None = None
    original_file_name: str | None = None


@dataclass(frozen=True)
class TopicGenerationInput:
    project_title: str
    project_description: str | None
    materials: list[TopicGenerationMaterial]
    candidate_count: int = 3


@dataclass(frozen=True)
class TopicCandidateDraft:
    title: str
    angle: str
    audience: str
    hook: str
    rationale: str


class LLMProvider(Protocol):
    provider_name: str
    provider_version: str

    def generate_topic_candidates(self, input: TopicGenerationInput) -> list[TopicCandidateDraft]:
        ...
