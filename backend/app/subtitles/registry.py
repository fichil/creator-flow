from app.subtitles.fake_subtitle_generator import FakeSubtitleGenerator
from app.subtitles.generator import SubtitleGenerator

_SUBTITLE_GENERATORS: dict[str, SubtitleGenerator] = {
    FakeSubtitleGenerator.generator_name: FakeSubtitleGenerator(),
}


def get_subtitle_generator(name: str = "fake_subtitle_generator") -> SubtitleGenerator:
    return _SUBTITLE_GENERATORS[name]
