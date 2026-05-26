# Product Specification

## Product Positioning

creator-flow is an open-source AI short-video content pipeline. It helps users turn explicitly imported ideas, chat summaries, text, images, screenshots, and links into review-ready 9:16 MP4 videos for short-video platforms.

The first publishing target is Douyin, but the product must remain platform-agnostic enough to support other publishing destinations later.

## User Problems

- Creators have useful raw material but need help converting it into repeatable short-video workflows.
- Programmers often solve real problems with AI but do not have a structured way to turn that process into content.
- Manual scripting, storyboarding, subtitle preparation, and video assembly are repetitive and time-consuming.
- Direct platform publishing is risky without clear review, approval, and privacy boundaries.

## Target Users

- Programmers documenting real development problems and solutions.
- Independent creators building technical or AI-assisted project logs.
- Open-source maintainers who want to convert project progress into short videos.
- Users who prefer explicit control over imported materials and final publishing decisions.

## Content Direction

The initial content direction is:

- Real programmer problems.
- AI-assisted solution walkthroughs.
- Open-source project development logs.

Trend content may be used as a supporting input for topic selection, but it must not replace the user's real experience and original materials as the main account narrative.

## Core User Workflow

1. The user creates a content project.
2. The user explicitly imports selected materials such as summaries, text, screenshots, images, or links.
3. The system helps generate topic options and a recommended angle.
4. The user reviews and edits the selected topic.
5. The system drafts a script, storyboard, asset plan, voiceover text, and subtitles.
6. The user reviews and edits the draft.
7. The system renders a 9:16 MP4 through the script + image or screenshot + TTS + subtitles + FFmpeg path.
8. The user reviews the rendered video.
9. The user explicitly confirms any publishing action.

## MVP Scope

- Content project management.
- Explicit material import.
- Topic ideation from user-provided materials and optional trend inputs.
- Script generation and editing.
- Storyboard and asset planning.
- TTS-backed voiceover generation through an abstract provider.
- Subtitle generation and editing.
- FFmpeg-based 9:16 MP4 rendering.
- Douyin publishing preparation with mandatory human review and confirmation.
- Provider abstractions for AI, media, rendering, trend sources, and publishing.

## Non-Goals

- No silent or automatic publishing.
- No automatic reading of ChatGPT history or other private accounts.
- No default pure AI text-to-video generation in the MVP path.
- No dependency on a single AI provider or publishing platform.
- No unmanaged storage of credentials, generated assets, private uploads, or local databases in Git.
- No production-scale multi-tenant SaaS assumptions in the MVP.

## Douyin Publishing Confirmation Principle

Any action that publishes, schedules, or otherwise sends content to Douyin or another platform must require user review and explicit confirmation. The system may prepare captions, metadata, files, and platform-specific checks, but it must not publish by default.

## Privacy and Material Import Boundary

The MVP only processes materials the user explicitly imports. It must not silently scan local files, read private chat history, scrape personal accounts, or infer consent from browser sessions. Imported materials, uploads, local databases, generated videos, audio, subtitles, and private notes must be excluded from Git.

## MVP Acceptance Criteria

- A user can create a content project from explicitly imported materials.
- A user can generate and edit a topic, script, storyboard, subtitles, and asset plan.
- A user can render a review-ready 9:16 MP4 using FFmpeg.
- Publishing to Douyin or any other platform requires a visible review step and explicit confirmation.
- External capabilities are accessed through provider interfaces.
- The default workflow avoids expensive pure AI text-to-video generation.
- Private materials, generated outputs, credentials, and local databases are not committed.
