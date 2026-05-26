# creator-flow

creator-flow is an open-source AI pipeline concept for turning user-provided ideas, notes, images, screenshots, links, and other materials into review-ready short videos.

## Status

Planning / Documentation Foundation.

This repository currently contains product and architecture documentation only. It does not yet provide a runnable application, backend service, frontend UI, video renderer, publishing integration, or provider implementation.

## Planned Capabilities

- Import user-selected chat summaries, text, images, screenshots, and links.
- Generate topic ideas, short-video scripts, storyboards, subtitles, and asset plans with AI providers.
- Render 9:16 MP4 videos through an FFmpeg-based pipeline.
- Support Douyin as the first publishing target while keeping the architecture open for other platforms.
- Keep LLM, image, TTS, rendering, trend, and publishing integrations behind provider interfaces.

These capabilities are planned and not yet implemented.

## Product Principles

- Publishing must remain human-in-the-loop. The MVP must not silently or automatically publish to Douyin or any other platform.
- User materials must be explicitly imported. The MVP must not automatically read private ChatGPT history or other private sources.
- Trend signals may support topic selection, but the account narrative should remain grounded in the user's real experience and original materials.
- The first content direction focuses on real programmer problems, AI-assisted solutions, and open-source project development logs.

## Privacy

creator-flow is intended to process only materials the user explicitly provides. Secrets, credentials, generated media, local databases, uploads, and private user data must not be committed to the repository.

## License

Apache-2.0. See `LICENSE`.
