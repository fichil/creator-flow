from app.renderers.fake_renderer import FakeRenderer
from app.renderers.renderer import Renderer

_RENDERERS: dict[str, Renderer] = {
    FakeRenderer.renderer_name: FakeRenderer(),
}


def get_renderer(name: str = "fake_renderer") -> Renderer:
    return _RENDERERS[name]
