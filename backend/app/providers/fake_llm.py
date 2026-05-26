import hashlib

from app.providers.llm import TopicCandidateDraft, TopicGenerationInput, TopicGenerationMaterial


class FakeLLMProvider:
    provider_name = "fake_llm"
    provider_version = "0.1"

    def generate_topic_candidates(self, input: TopicGenerationInput) -> list[TopicCandidateDraft]:
        candidate_count = min(max(input.candidate_count, 1), 5)
        seed = _stable_seed(input)
        material_summary = _summarize_materials(input.materials)
        project_title = _clean(input.project_title) or "Untitled Project"
        description_hint = _clean(input.project_description) or "imported creator materials"

        templates = [
            (
                "Problem-first",
                "Turn a concrete friction point into a short, useful story",
                "Developers and creators facing similar workflow blocks",
                "Here is the small workflow problem that quietly slowed this project down.",
            ),
            (
                "Before-and-after",
                "Show the gap between the messy input and the clearer next step",
                "Creators who want practical AI-assisted production habits",
                "The useful part was not the tool itself, but the decision it made easier.",
            ),
            (
                "Build log",
                "Frame the material as a local product development note",
                "Independent builders tracking real project progress",
                "This started as a small project note, but it exposed a reusable pattern.",
            ),
            (
                "Checklist",
                "Convert the imported notes into an actionable review checklist",
                "Busy technical creators who need repeatable execution steps",
                "Before generating anything, these are the inputs worth checking first.",
            ),
            (
                "Tradeoff",
                "Explain one product or engineering tradeoff behind the current workflow",
                "Viewers interested in how creator tools are designed",
                "The interesting choice was what the workflow deliberately refused to automate.",
            ),
        ]

        start = int(seed[:2], 16) % len(templates)
        ordered = templates[start:] + templates[:start]

        candidates: list[TopicCandidateDraft] = []
        for index, (label, angle, audience, hook) in enumerate(ordered[:candidate_count], start=1):
            digest = seed[(index - 1) * 4 : index * 4]
            candidates.append(
                TopicCandidateDraft(
                    title=f"{project_title}: {label} topic {digest}",
                    angle=angle,
                    audience=audience,
                    hook=hook,
                    rationale=(
                        f"Based on {material_summary} for '{project_title}'. "
                        f"The project description suggests: {description_hint}."
                    ),
                )
            )
        return candidates


def _stable_seed(input: TopicGenerationInput) -> str:
    parts = [_clean(input.project_title), _clean(input.project_description), str(input.candidate_count)]
    for material in sorted(input.materials, key=lambda item: item.id):
        parts.extend(
            [
                str(material.id),
                _clean(material.material_type),
                _clean(material.title),
                _clean(material.text_content),
                _clean(material.source_url),
                _clean(material.original_file_name),
            ]
        )
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def _summarize_materials(materials: list[TopicGenerationMaterial]) -> str:
    if not materials:
        return "0 imported materials"

    counts: dict[str, int] = {}
    for material in materials:
        counts[material.material_type] = counts.get(material.material_type, 0) + 1
    segments = [f"{count} {material_type}" for material_type, count in sorted(counts.items())]
    return f"{len(materials)} imported materials ({', '.join(segments)})"


def _clean(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.strip().split())
