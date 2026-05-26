from app.providers.fake_llm import FakeLLMProvider
from app.providers.llm import (
    ScriptGenerationInput,
    SelectedScriptDraft,
    SelectedTopicCandidate,
    StoryboardGenerationInput,
    TopicGenerationInput,
    TopicGenerationMaterial,
)


def _input(candidate_count: int = 3) -> TopicGenerationInput:
    return TopicGenerationInput(
        project_title="Creator workflow",
        project_description="Turn imported notes into reviewable short video ideas.",
        candidate_count=candidate_count,
        materials=[
            TopicGenerationMaterial(
                id=1,
                material_type="text",
                title="Build note",
                text_content="A deterministic planning workflow is easier to test.",
            ),
            TopicGenerationMaterial(
                id=2,
                material_type="image",
                title="Screenshot",
                original_file_name="planning-board.png",
            ),
        ],
    )


def _script_input(script_count: int = 2) -> ScriptGenerationInput:
    return ScriptGenerationInput(
        project_title="Creator workflow",
        project_description="Turn imported notes into reviewable short video ideas.",
        script_count=script_count,
        topic_candidate=SelectedTopicCandidate(
            id=10,
            title="Creator workflow: Problem-first topic",
            angle="Turn a concrete friction point into a short, useful story",
            audience="Developers and creators facing similar workflow blocks",
            hook="Here is the small workflow problem that quietly slowed this project down.",
            rationale="Based on explicit imported materials.",
        ),
        materials=[
            TopicGenerationMaterial(
                id=1,
                material_type="text",
                title="Build note",
                text_content="A deterministic planning workflow is easier to test.",
            ),
            TopicGenerationMaterial(
                id=2,
                material_type="image",
                title="Screenshot",
                original_file_name="planning-board.png",
            ),
        ],
    )


def _storyboard_input(storyboard_count: int = 1) -> StoryboardGenerationInput:
    return StoryboardGenerationInput(
        project_title="Creator workflow",
        project_description="Turn imported notes into reviewable short video ideas.",
        storyboard_count=storyboard_count,
        topic_candidate=SelectedTopicCandidate(
            id=10,
            title="Creator workflow: Problem-first topic",
            angle="Turn a concrete friction point into a short, useful story",
            audience="Developers and creators facing similar workflow blocks",
            hook="Here is the small workflow problem that quietly slowed this project down.",
            rationale="Based on explicit imported materials.",
        ),
        script_draft=SelectedScriptDraft(
            id=20,
            title="Creator workflow: Concise explainer script",
            opening_hook="Here is the small workflow problem that quietly slowed this project down.",
            body="1. Start from the selected topic.\n2. Ground the script in imported material.",
            call_to_action="Save this workflow note before the next planning pass.",
            estimated_duration_seconds=55,
            rationale="Based on selected topic candidate 10 and explicit imported materials.",
        ),
        materials=[
            TopicGenerationMaterial(
                id=1,
                material_type="text",
                title="Build note",
                text_content="A deterministic planning workflow is easier to test.",
            ),
            TopicGenerationMaterial(
                id=2,
                material_type="image",
                title="Screenshot",
                original_file_name="planning-board.png",
            ),
        ],
    )


def test_fake_llm_provider_outputs_deterministic_candidates():
    provider = FakeLLMProvider()

    first = provider.generate_topic_candidates(_input())
    second = provider.generate_topic_candidates(_input())

    assert first == second
    assert len(first) == 3
    assert first[0].title
    assert first[0].rationale


def test_fake_llm_provider_does_not_need_api_key(monkeypatch):
    provider = FakeLLMProvider()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    candidates = provider.generate_topic_candidates(_input())

    assert len(candidates) == 3


def test_fake_llm_provider_ignores_ai_key_environment(monkeypatch):
    provider = FakeLLMProvider()
    monkeypatch.setenv("OPENAI_API_KEY", "first-value")
    first = provider.generate_topic_candidates(_input())
    monkeypatch.setenv("OPENAI_API_KEY", "second-value")
    second = provider.generate_topic_candidates(_input())

    assert first == second


def test_fake_llm_provider_does_not_read_image_file_content(monkeypatch):
    provider = FakeLLMProvider()

    def fail_if_opened(*args, **kwargs):
        raise AssertionError("FakeLLMProvider must not read local image files")

    monkeypatch.setattr("builtins.open", fail_if_opened)

    candidates = provider.generate_topic_candidates(_input())

    assert len(candidates) == 3
    assert "image" in candidates[0].rationale


def test_fake_llm_provider_clamps_candidate_count():
    provider = FakeLLMProvider()

    assert len(provider.generate_topic_candidates(_input(candidate_count=0))) == 1
    assert len(provider.generate_topic_candidates(_input(candidate_count=6))) == 5


def test_fake_llm_provider_outputs_deterministic_script_drafts():
    provider = FakeLLMProvider()

    first = provider.generate_script_drafts(_script_input())
    second = provider.generate_script_drafts(_script_input())

    assert first == second
    assert len(first) == 2
    assert first[0].title
    assert first[0].opening_hook
    assert first[0].body
    assert first[0].estimated_duration_seconds > 0


def test_fake_llm_provider_script_generation_does_not_need_api_key(monkeypatch):
    provider = FakeLLMProvider()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    drafts = provider.generate_script_drafts(_script_input())

    assert len(drafts) == 2


def test_fake_llm_provider_script_generation_ignores_ai_key_environment(monkeypatch):
    provider = FakeLLMProvider()
    monkeypatch.setenv("OPENAI_API_KEY", "first-value")
    first = provider.generate_script_drafts(_script_input())
    monkeypatch.setenv("OPENAI_API_KEY", "second-value")
    second = provider.generate_script_drafts(_script_input())

    assert first == second


def test_fake_llm_provider_script_generation_does_not_read_image_file_content(monkeypatch):
    provider = FakeLLMProvider()

    def fail_if_opened(*args, **kwargs):
        raise AssertionError("FakeLLMProvider must not read local image files")

    monkeypatch.setattr("builtins.open", fail_if_opened)

    drafts = provider.generate_script_drafts(_script_input())

    assert len(drafts) == 2
    assert "image" in drafts[0].body


def test_fake_llm_provider_clamps_script_count():
    provider = FakeLLMProvider()

    assert len(provider.generate_script_drafts(_script_input(script_count=0))) == 1
    assert len(provider.generate_script_drafts(_script_input(script_count=4))) == 3


def test_fake_llm_provider_outputs_deterministic_storyboard_drafts():
    provider = FakeLLMProvider()

    first = provider.generate_storyboard_drafts(_storyboard_input())
    second = provider.generate_storyboard_drafts(_storyboard_input())

    assert first == second
    assert len(first) == 1
    assert first[0].title
    assert first[0].summary
    assert first[0].visual_style
    assert len(first[0].scenes) >= 2


def test_fake_llm_provider_storyboard_generation_does_not_need_api_key(monkeypatch):
    provider = FakeLLMProvider()
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    storyboards = provider.generate_storyboard_drafts(_storyboard_input())

    assert len(storyboards) == 1


def test_fake_llm_provider_storyboard_generation_ignores_ai_key_environment(monkeypatch):
    provider = FakeLLMProvider()
    monkeypatch.setenv("OPENAI_API_KEY", "first-value")
    first = provider.generate_storyboard_drafts(_storyboard_input())
    monkeypatch.setenv("OPENAI_API_KEY", "second-value")
    second = provider.generate_storyboard_drafts(_storyboard_input())

    assert first == second


def test_fake_llm_provider_storyboard_generation_does_not_read_image_file_content(monkeypatch):
    provider = FakeLLMProvider()

    def fail_if_opened(*args, **kwargs):
        raise AssertionError("FakeLLMProvider must not read local image files")

    monkeypatch.setattr("builtins.open", fail_if_opened)

    storyboards = provider.generate_storyboard_drafts(_storyboard_input())

    assert len(storyboards) == 1
    assert "image" in storyboards[0].summary


def test_fake_llm_provider_clamps_storyboard_count():
    provider = FakeLLMProvider()

    assert len(provider.generate_storyboard_drafts(_storyboard_input(storyboard_count=0))) == 1
    assert len(provider.generate_storyboard_drafts(_storyboard_input(storyboard_count=3))) == 2


def test_fake_llm_provider_storyboard_scenes_are_orderable_and_have_positive_duration():
    provider = FakeLLMProvider()

    storyboard = provider.generate_storyboard_drafts(_storyboard_input())[0]

    assert len(storyboard.scenes) >= 2
    assert [scene.scene_title.split(".", maxsplit=1)[0] for scene in storyboard.scenes] == ["1", "2", "3"]
    assert all(scene.estimated_duration_seconds > 0 for scene in storyboard.scenes)
