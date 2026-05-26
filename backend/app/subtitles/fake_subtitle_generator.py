from app.subtitles.generator import SubtitleCueDraft, SubtitleInput


class FakeSubtitleGenerator:
    generator_name = "fake_subtitle_generator"
    generator_version = "0.1"

    def generate(self, input: SubtitleInput) -> list[SubtitleCueDraft]:
        cues: list[SubtitleCueDraft] = []
        current_time = 0
        for cue_order, scene in enumerate(input.scenes, start=1):
            end_time = current_time + scene.estimated_duration_seconds
            cues.append(
                SubtitleCueDraft(
                    cue_order=cue_order,
                    start_time_seconds=current_time,
                    end_time_seconds=end_time,
                    text=scene.narration.strip(),
                )
            )
            current_time = end_time
        return cues
