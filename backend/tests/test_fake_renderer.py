from app.renderers import FakeRenderer, RenderInput, RenderScene, RenderStoryboard


def _render_input() -> RenderInput:
    return RenderInput(
        project_id=7,
        render_job_id=11,
        project_title="Rendering workflow",
        project_description="Fake rendering metadata only.",
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
    assert first.file_name == "project-7-render-11.mp4"
    assert first.storage_path == "data/local/fake-renders/project-7/render-11.mp4"


def test_fake_renderer_does_not_need_api_key(monkeypatch):
    renderer = FakeRenderer()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    artifact = renderer.render(_render_input())

    assert artifact.mime_type == "video/mp4"


def test_fake_renderer_ignores_ai_key_environment(monkeypatch):
    renderer = FakeRenderer()
    monkeypatch.setenv("OPENAI_API_KEY", "first-value")
    first = renderer.render(_render_input())
    monkeypatch.setenv("OPENAI_API_KEY", "second-value")
    second = renderer.render(_render_input())

    assert first == second


def test_fake_renderer_does_not_read_image_file_content(monkeypatch):
    renderer = FakeRenderer()

    def fail_if_opened(*args, **kwargs):
        raise AssertionError("FakeRenderer must not read local image files")

    monkeypatch.setattr("builtins.open", fail_if_opened)

    artifact = renderer.render(_render_input())

    assert artifact.storage_path.endswith("render-11.mp4")


def test_fake_renderer_does_not_call_media_generation_commands(monkeypatch):
    renderer = FakeRenderer()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("FakeRenderer must not call media generation commands")

    monkeypatch.setattr("subprocess.run", fail_if_called)
    monkeypatch.setattr("subprocess.Popen", fail_if_called)

    artifact = renderer.render(_render_input())

    assert artifact.file_size_bytes == 30 * 1024


def test_fake_renderer_metadata_uses_scene_duration_and_fixed_video_shape():
    renderer = FakeRenderer()

    artifact = renderer.render(_render_input())

    assert artifact.duration_seconds == 30
    assert artifact.file_size_bytes == 30 * 1024
    assert artifact.width == 1080
    assert artifact.height == 1920
    assert artifact.mime_type == "video/mp4"
