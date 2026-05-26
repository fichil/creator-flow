import json
import tempfile
from pathlib import Path

from app.renderers import FakeRenderer, RenderInput, RenderScene, RenderStoryboard


def _render_input(preview_output_dir: Path | None = None) -> RenderInput:
    return RenderInput(
        project_id=7,
        render_job_id=11,
        selected_subtitle_draft_id=13,
        project_title="Rendering workflow",
        project_description="Fake rendering metadata only.",
        preview_output_dir=preview_output_dir or Path(tempfile.gettempdir()) / "creator-flow-test-render-previews",
        storyboard=RenderStoryboard(
            id=5,
            title="Rendering workflow storyboard",
            summary="A selected storyboard for fake rendering.",
            visual_style="Clean screen-recording style",
        ),
        scenes=[
            RenderScene(
                id=1,
                scene_order=1,
                scene_title="Intro",
                narration="Start with the selected storyboard.",
                visual_description="Show the storyboard title and first scene.",
                on_screen_text="Intro",
                estimated_duration_seconds=12,
                source_material_id=3,
            ),
            RenderScene(
                id=2,
                scene_order=2,
                scene_title="Takeaway",
                narration="Close with a deterministic fake artifact.",
                visual_description="Show metadata instead of real media output.",
                on_screen_text="Metadata only",
                estimated_duration_seconds=18,
                source_material_id=None,
            ),
        ],
    )


def test_fake_renderer_outputs_deterministic_artifact_metadata():
    renderer = FakeRenderer()

    first = renderer.render(_render_input())
    second = renderer.render(_render_input())

    assert first == second
    assert first.artifact_type == "fake_preview_manifest"
    assert first.file_name == "project-7-render-11-preview-manifest.json"
    assert first.storage_path == "data/local/render_previews/project-7/project-7-render-11-preview-manifest.json"
    assert first.mime_type == "application/json"


def test_fake_renderer_does_not_need_api_key(monkeypatch, tmp_path):
    renderer = FakeRenderer()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    artifact = renderer.render(_render_input(tmp_path))

    assert artifact.mime_type == "application/json"


def test_fake_renderer_ignores_ai_key_environment(monkeypatch):
    renderer = FakeRenderer()
    monkeypatch.setenv("OPENAI_API_KEY", "first-value")
    first = renderer.render(_render_input())
    monkeypatch.setenv("OPENAI_API_KEY", "second-value")
    second = renderer.render(_render_input())

    assert first == second


def test_fake_renderer_does_not_read_image_file_content(monkeypatch, tmp_path):
    renderer = FakeRenderer()

    def fail_if_opened(*args, **kwargs):
        raise AssertionError("FakeRenderer must not read local image files")

    monkeypatch.setattr("builtins.open", fail_if_opened)

    artifact = renderer.render(_render_input(tmp_path))

    assert artifact.storage_path.endswith("render-11-preview-manifest.json")


def test_fake_renderer_does_not_call_media_generation_commands(monkeypatch, tmp_path):
    renderer = FakeRenderer()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("FakeRenderer must not call media generation commands")

    monkeypatch.setattr("subprocess.run", fail_if_called)
    monkeypatch.setattr("subprocess.Popen", fail_if_called)

    artifact = renderer.render(_render_input(tmp_path))

    assert artifact.file_size_bytes > 0


def test_fake_renderer_metadata_uses_scene_duration_and_fixed_video_shape(tmp_path):
    renderer = FakeRenderer()

    artifact = renderer.render(_render_input(tmp_path))

    assert artifact.duration_seconds == 30
    assert artifact.file_size_bytes > 0
    assert artifact.width == 1080
    assert artifact.height == 1920
    assert artifact.mime_type == "application/json"


def test_fake_renderer_writes_preview_manifest_metadata(tmp_path):
    renderer = FakeRenderer()

    artifact = renderer.render(_render_input(tmp_path))
    manifest_path = tmp_path / "project-7" / "project-7-render-11-preview-manifest.json"

    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["artifact_type"] == "fake_preview_manifest"
    assert manifest["project_id"] == 7
    assert manifest["render_job_id"] == 11
    assert manifest["selected_storyboard_id"] == 5
    assert manifest["selected_subtitle_draft_id"] == 13
    assert manifest["duration_seconds"] == 30
    assert artifact.checksum_sha256
