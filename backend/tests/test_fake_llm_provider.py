from app.providers.fake_llm import FakeLLMProvider
from app.providers.llm import TopicGenerationInput, TopicGenerationMaterial


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
