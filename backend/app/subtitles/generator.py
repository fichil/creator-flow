from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SubtitleScene:
    id: int
    scene_order: int
    narration: str
    estimated_duration_seconds: int


@dataclass(frozen=True)
class SubtitleInput:
    project_id: int
    project_title: str
    project_description: str | None
    script_draft_id: int
    storyboard_draft_id: int
    scenes: list[SubtitleScene]


@dataclass(frozen=True)
class SubtitleCueDraft:
    cue_order: int
    start_time_seconds: int
    end_time_seconds: int
    text: str


class SubtitleGenerator(Protocol):
    generator_name: str
    generator_version: str

    def generate(self, input: SubtitleInput) -> list[SubtitleCueDraft]:
        ...
