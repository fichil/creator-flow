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


@dataclass(frozen=True)
class SelectedTopicCandidate:
    id: int
    title: str
    angle: str
    audience: str
    hook: str
    rationale: str


@dataclass(frozen=True)
class ScriptGenerationInput:
    project_title: str
    project_description: str | None
    topic_candidate: SelectedTopicCandidate
    materials: list[TopicGenerationMaterial]
    script_count: int = 2


@dataclass(frozen=True)
class ScriptDraftCandidate:
    title: str
    opening_hook: str
    body: str
    call_to_action: str
    estimated_duration_seconds: int
    rationale: str


@dataclass(frozen=True)
class SelectedScriptDraft:
    id: int
    title: str
    opening_hook: str
    body: str
    call_to_action: str
    estimated_duration_seconds: int
    rationale: str


@dataclass(frozen=True)
class StoryboardGenerationInput:
    project_title: str
    project_description: str | None
    topic_candidate: SelectedTopicCandidate
    script_draft: SelectedScriptDraft
    materials: list[TopicGenerationMaterial]
    storyboard_count: int = 1


@dataclass(frozen=True)
class StoryboardSceneCandidate:
    scene_title: str
    narration: str
    visual_description: str
    on_screen_text: str
    estimated_duration_seconds: int
    source_material_id: int | None = None


@dataclass(frozen=True)
class StoryboardDraftCandidate:
    title: str
    summary: str
    visual_style: str
    scenes: list[StoryboardSceneCandidate]


class LLMProvider(Protocol):
    provider_name: str
    provider_version: str

    def generate_topic_candidates(self, input: TopicGenerationInput) -> list[TopicCandidateDraft]:
        ...

    def generate_script_drafts(self, input: ScriptGenerationInput) -> list[ScriptDraftCandidate]:
        ...

    def generate_storyboard_drafts(self, input: StoryboardGenerationInput) -> list[StoryboardDraftCandidate]:
        ...
