from app.renderers.renderer import RenderInput, RenderOutput


class FakeRenderer:
    renderer_name = "fake_renderer"
    renderer_version = "0.1"

    def render(self, input: RenderInput) -> RenderOutput:
        duration_seconds = sum(scene.estimated_duration_seconds for scene in input.scenes)
        file_name = f"project-{input.project_id}-render-{input.render_job_id}.mp4"
        storage_path = f"data/local/fake-renders/project-{input.project_id}/render-{input.render_job_id}.mp4"

        return RenderOutput(
            file_name=file_name,
            mime_type="video/mp4",
            file_size_bytes=duration_seconds * 1024,
            duration_seconds=duration_seconds,
            width=1080,
            height=1920,
            storage_path=storage_path,
        )
