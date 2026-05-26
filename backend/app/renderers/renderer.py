from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class RenderStoryboard:
    id: int
    title: str
    summary: str
    visual_style: str


@dataclass(frozen=True)
class RenderScene:
    id: int
    scene_order: int
    scene_title: str
    narration: str
    visual_description: str
    on_screen_text: str
    estimated_duration_seconds: int
    source_material_id: int | None = None


@dataclass(frozen=True)
class RenderInput:
    project_id: int
    render_job_id: int
    selected_subtitle_draft_id: int | None
    project_title: str
    project_description: str | None
    storyboard: RenderStoryboard
    scenes: list[RenderScene]
    preview_output_dir: Path | None = None
    requested_format: str = "mp4"
    requested_aspect_ratio: str = "9:16"
    requested_resolution: str = "1080x1920"


@dataclass(frozen=True)
class RenderOutput:
    artifact_type: str
    file_name: str
    mime_type: str
    file_size_bytes: int
    duration_seconds: int
    width: int
    height: int
    storage_path: str
    checksum_sha256: str


class Renderer(Protocol):
    renderer_name: str
    renderer_version: str

    def render(self, input: RenderInput) -> RenderOutput:
        ...
