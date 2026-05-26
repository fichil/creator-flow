# ADR 0001: Product Positioning

## Status

Accepted

## Context

creator-flow starts with Douyin as the first publishing platform, but the core user problem is broader than one platform. Creators need a repeatable way to turn explicitly imported materials into short-video projects that can later be adapted to different destinations.

Binding the product only to Douyin would make early implementation faster, but it would also mix platform-specific publishing details into the creative workflow and make future expansion harder.

## Decision

creator-flow will be positioned as a general AI short-video content pipeline rather than a Douyin-only tool.

Douyin will be the first target platform, but platform-specific logic must live behind provider interfaces and publishing preparation modules.

## Consequences

- The product can support additional short-video platforms later.
- Core concepts such as materials, topics, scripts, storyboards, render jobs, and publish intents remain reusable.
- The MVP must avoid naming, data model, and workflow choices that assume Douyin is the only destination.
- Some early design work is slightly more abstract, but the architecture remains healthier for open-source contributors.
