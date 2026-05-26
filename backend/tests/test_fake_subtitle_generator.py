from app.subtitles import FakeSubtitleGenerator, SubtitleInput, SubtitleScene


def _subtitle_input() -> SubtitleInput:
    return SubtitleInput(
        project_id=7,
        project_title="Subtitle workflow",
        project_description="Fake subtitle metadata only.",
        script_draft_id=5,
        storyboard_draft_id=11,
        scenes=[
            SubtitleScene(
                id=1,
                scene_order=1,
                narration="Start with the selected storyboard.",
                estimated_duration_seconds=12,
            ),
            SubtitleScene(
                id=2,
                scene_order=2,
                narration="Close with deterministic cue metadata.",
                estimated_duration_seconds=18,
            ),
        ],
    )


def test_fake_subtitle_generator_outputs_deterministic_cues():
    generator = FakeSubtitleGenerator()

    first = generator.generate(_subtitle_input())
    second = generator.generate(_subtitle_input())

    assert first == second
    assert first[0].cue_order == 1
    assert first[0].start_time_seconds == 0
    assert first[0].end_time_seconds == 12
    assert first[1].start_time_seconds == 12
    assert first[1].end_time_seconds == 30


def test_fake_subtitle_generator_uses_scene_narration_as_text():
    generator = FakeSubtitleGenerator()

    cues = generator.generate(_subtitle_input())

    assert cues[0].text == "Start with the selected storyboard."
    assert cues[1].text == "Close with deterministic cue metadata."


def test_fake_subtitle_generator_does_not_need_api_key(monkeypatch):
    generator = FakeSubtitleGenerator()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    cues = generator.generate(_subtitle_input())

    assert len(cues) == 2


def test_fake_subtitle_generator_ignores_ai_key_environment(monkeypatch):
    generator = FakeSubtitleGenerator()
    monkeypatch.setenv("OPENAI_API_KEY", "first-value")
    first = generator.generate(_subtitle_input())
    monkeypatch.setenv("OPENAI_API_KEY", "second-value")
    second = generator.generate(_subtitle_input())

    assert first == second


def test_fake_subtitle_generator_does_not_create_files(monkeypatch):
    generator = FakeSubtitleGenerator()

    def fail_if_opened(*args, **kwargs):
        raise AssertionError("FakeSubtitleGenerator must not create subtitle files")

    monkeypatch.setattr("builtins.open", fail_if_opened)

    cues = generator.generate(_subtitle_input())

    assert cues[0].text


def test_fake_subtitle_generator_does_not_call_media_generation_commands(monkeypatch):
    generator = FakeSubtitleGenerator()

    def fail_if_called(*args, **kwargs):
        raise AssertionError("FakeSubtitleGenerator must not call media generation commands")

    monkeypatch.setattr("subprocess.run", fail_if_called)
    monkeypatch.setattr("subprocess.Popen", fail_if_called)

    cues = generator.generate(_subtitle_input())

    assert cues[-1].end_time_seconds == 30
