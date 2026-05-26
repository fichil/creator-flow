import hashlib

from app.providers.llm import (
    ScriptDraftCandidate,
    ScriptGenerationInput,
    StoryboardDraftCandidate,
    StoryboardGenerationInput,
    StoryboardSceneCandidate,
    TopicCandidateDraft,
    TopicGenerationInput,
    TopicGenerationMaterial,
)


class FakeLLMProvider:
    provider_name = "fake_llm"
    provider_version = "0.1"

    def generate_topic_candidates(self, input: TopicGenerationInput) -> list[TopicCandidateDraft]:
        candidate_count = min(max(input.candidate_count, 1), 5)
        seed = _stable_topic_seed(input)
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

    def generate_script_drafts(self, input: ScriptGenerationInput) -> list[ScriptDraftCandidate]:
        script_count = min(max(input.script_count, 1), 3)
        seed = _stable_script_seed(input)
        material_summary = _summarize_materials(input.materials)
        project_title = _clean(input.project_title) or "Untitled Project"
        topic = input.topic_candidate
        topic_title = _clean(topic.title) or "Selected topic"
        hook = _clean(topic.hook) or "Here is the core idea worth watching."

        templates = [
            (
                "Concise explainer",
                55,
                "Explain the selected angle with one concrete before-and-after moment.",
                "Save this workflow note before the next planning pass.",
            ),
            (
                "Build-log narrative",
                70,
                "Walk through the project context, the decision point, and the reusable lesson.",
                "Pick one imported note and turn it into the next draft.",
            ),
            (
                "Checklist walkthrough",
                60,
                "Convert the selected topic into three practical checks viewers can reuse.",
                "Use the checklist on your own imported material.",
            ),
        ]

        start = int(seed[:2], 16) % len(templates)
        ordered = templates[start:] + templates[:start]

        drafts: list[ScriptDraftCandidate] = []
        for index, (label, seconds, body_direction, call_to_action) in enumerate(ordered[:script_count], start=1):
            digest = seed[(index - 1) * 4 : index * 4]
            body = (
                f"1. Start from the selected topic: {topic_title}.\n"
                f"2. Use the angle '{_clean(topic.angle)}' for {_clean(topic.audience)}.\n"
                f"3. {body_direction}\n"
                f"4. Ground the script in {material_summary}."
            )
            drafts.append(
                ScriptDraftCandidate(
                    title=f"{project_title}: {label} script {digest}",
                    opening_hook=hook,
                    body=body,
                    call_to_action=call_to_action,
                    estimated_duration_seconds=seconds,
                    rationale=(
                        f"Based on selected topic candidate {topic.id} and {material_summary}. "
                        f"Topic rationale: {_clean(topic.rationale)}."
                    ),
                )
            )
        return drafts

    def generate_storyboard_drafts(self, input: StoryboardGenerationInput) -> list[StoryboardDraftCandidate]:
        storyboard_count = min(max(input.storyboard_count, 1), 2)
        seed = _stable_storyboard_seed(input)
        material_summary = _summarize_materials(input.materials)
        project_title = _clean(input.project_title) or "Untitled Project"
        topic = input.topic_candidate
        script = input.script_draft
        topic_title = _clean(topic.title) or "Selected topic"
        script_title = _clean(script.title) or "Selected script"

        templates = [
            (
                "Practical walkthrough",
                "Clean screen-recording style with focused captions and simple transitions",
                [
                    (
                        "Set up the problem",
                        _clean(script.opening_hook) or _clean(topic.hook) or "Start with the core workflow problem.",
                        "Open on the project context and the imported material that motivated the story.",
                        "The problem",
                        12,
                    ),
                    (
                        "Show the decision",
                        f"Use the selected angle: {_clean(topic.angle)}.",
                        "Move from the raw note to a clear planning decision with one highlighted detail.",
                        "The decision",
                        18,
                    ),
                    (
                        "Close with the takeaway",
                        _clean(script.call_to_action) or "Turn the lesson into the next repeatable step.",
                        "End on a concise checklist-style frame that reinforces the reusable workflow.",
                        "Try it next",
                        14,
                    ),
                ],
            ),
            (
                "Build-log storyboard",
                "Notebook and product UI style with grounded, low-motion visual beats",
                [
                    (
                        "Context snapshot",
                        f"This draft starts from {script_title}.",
                        "Show the project title, selected topic, and one imported note as a calm setup.",
                        "Context",
                        10,
                    ),
                    (
                        "Script beat",
                        _first_script_line(script.body),
                        "Translate the first script beat into a clear visual contrast between before and after.",
                        "Script beat",
                        20,
                    ),
                    (
                        "Source-backed lesson",
                        f"Ground the story in {material_summary}.",
                        "Show source material references as small labels so the draft remains traceable.",
                        "Source-backed",
                        16,
                    ),
                ],
            ),
        ]

        start = int(seed[:2], 16) % len(templates)
        ordered = templates[start:] + templates[:start]
        sorted_materials = sorted(input.materials, key=lambda item: item.id)

        storyboards: list[StoryboardDraftCandidate] = []
        for index, (label, visual_style, scene_templates) in enumerate(ordered[:storyboard_count], start=1):
            digest = seed[(index - 1) * 4 : index * 4]
            scenes: list[StoryboardSceneCandidate] = []
            for scene_index, (scene_title, narration, visual_description, on_screen_text, seconds) in enumerate(
                scene_templates,
                start=1,
            ):
                source_material_id = None
                if sorted_materials:
                    source_material_id = sorted_materials[(scene_index - 1) % len(sorted_materials)].id
                scenes.append(
                    StoryboardSceneCandidate(
                        scene_title=f"{scene_index}. {scene_title}",
                        narration=narration,
                        visual_description=visual_description,
                        on_screen_text=on_screen_text,
                        estimated_duration_seconds=max(seconds, 1),
                        source_material_id=source_material_id,
                    )
                )

            storyboards.append(
                StoryboardDraftCandidate(
                    title=f"{project_title}: {label} storyboard {digest}",
                    summary=(
                        f"Storyboard for '{topic_title}' using selected script draft {script.id} "
                        f"and {material_summary}."
                    ),
                    visual_style=visual_style,
                    scenes=scenes,
                )
            )
        return storyboards


def _stable_topic_seed(input: TopicGenerationInput) -> str:
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


def _stable_script_seed(input: ScriptGenerationInput) -> str:
    topic = input.topic_candidate
    parts = [
        _clean(input.project_title),
        _clean(input.project_description),
        str(input.script_count),
        str(topic.id),
        _clean(topic.title),
        _clean(topic.angle),
        _clean(topic.audience),
        _clean(topic.hook),
        _clean(topic.rationale),
    ]
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


def _stable_storyboard_seed(input: StoryboardGenerationInput) -> str:
    topic = input.topic_candidate
    script = input.script_draft
    parts = [
        _clean(input.project_title),
        _clean(input.project_description),
        str(input.storyboard_count),
        str(topic.id),
        _clean(topic.title),
        _clean(topic.angle),
        _clean(topic.audience),
        _clean(topic.hook),
        _clean(topic.rationale),
        str(script.id),
        _clean(script.title),
        _clean(script.opening_hook),
        _clean(script.body),
        _clean(script.call_to_action),
        str(script.estimated_duration_seconds),
        _clean(script.rationale),
    ]
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


def _first_script_line(value: str | None) -> str:
    cleaned = _clean(value)
    if not cleaned:
        return "Show the first concrete beat from the selected script."
    return cleaned.split(". ", maxsplit=1)[0].strip() or cleaned
