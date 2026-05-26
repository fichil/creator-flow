import hashlib
import json
from pathlib import Path

from app.renderers.renderer import RenderInput, RenderOutput


class FakeRenderer:
    renderer_name = "fake_renderer"
    renderer_version = "0.1"

    def render(self, input: RenderInput) -> RenderOutput:
        duration_seconds = sum(scene.estimated_duration_seconds for scene in input.scenes)
        width = 1080
        height = 1920
        file_name = f"project-{input.project_id}-render-{input.render_job_id}-preview-manifest.json"
        storage_path = f"data/local/render_previews/project-{input.project_id}/{file_name}"
        manifest = {
            "artifact_type": "fake_preview_manifest",
            "created_at": "1970-01-01T00:00:00Z",
            "duration_seconds": duration_seconds,
            "height": height,
            "project_id": input.project_id,
            "render_job_id": input.render_job_id,
            "renderer_name": self.renderer_name,
            "renderer_version": self.renderer_version,
            "requested_aspect_ratio": input.requested_aspect_ratio,
            "requested_format": input.requested_format,
            "requested_resolution": input.requested_resolution,
            "selected_storyboard_id": input.storyboard.id,
            "selected_subtitle_draft_id": input.selected_subtitle_draft_id,
            "storage_path": storage_path,
            "width": width,
        }
        manifest_bytes = (json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        checksum = hashlib.sha256(manifest_bytes).hexdigest()
        preview_output_dir = input.preview_output_dir or Path("data/local/render_previews")
        manifest_path = preview_output_dir / f"project-{input.project_id}" / file_name
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_bytes(manifest_bytes)

        return RenderOutput(
            artifact_type="fake_preview_manifest",
            file_name=file_name,
            mime_type="application/json",
            file_size_bytes=len(manifest_bytes),
            duration_seconds=duration_seconds,
            width=width,
            height=height,
            storage_path=storage_path,
            checksum_sha256=checksum,
        )
